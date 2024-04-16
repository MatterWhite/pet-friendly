from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional, List

import dateparser

from db import db_conn
from models.dog import Dog
from models.user import User
from models.user_type import UserType
from models.walk_zone import WalkZone


@dataclass(frozen=True)
class WalkRequest:
    _id: int
    start_at: datetime.datetime
    end_at: datetime.datetime
    price: int
    issuer: User
    executor: Optional[User]
    transfer_addr: str
    is_started: bool
    is_finished: bool
    dogs: List[Dog]
    walk_zones: List[WalkZone]

    def assign_zones(self, zone_ids: List[int]):
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('DELETE FROM walk_request_zones '
                            'WHERE request_id=%s;', (self._id,))
                for zone_id in zone_ids:
                    cur.execute('INSERT INTO walk_request_zones '
                                '   (request_id, zone_id) '
                                'VALUES '
                                '   (%s, %s);', (self._id, zone_id))
            db.commit()

    def assign_executor(self, executor_id):
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('UPDATE walk_requests '
                            'SET executor_id=%s '
                            'WHERE id=%s '
                            'AND NOT is_started '
                            'AND executor_id IS NULL;', (executor_id, self._id))
            db.commit()

    def begin(self):
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('UPDATE walk_requests '
                            'SET is_started=TRUE '
                            'WHERE id=%s;', (self._id,))
            db.commit()

    def finish(self):
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('UPDATE walk_requests '
                            'SET is_finished=TRUE '
                            'WHERE id=%s;', (self._id,))
            db.commit()

    @staticmethod
    def fetch_one(**kvargs) -> Optional[WalkRequest]:
        res = WalkRequest.fetch_many(1, **kvargs)
        if len(res) == 0:
            return None
        return res[0]

    @staticmethod
    def fetch_many(limit: Optional[int] = None, **kvargs) -> List[WalkRequest]:
        key, value = list(kvargs.items())[0]

        filter_ql = ''
        args = ()
        for k, v in kvargs.items():
            if len(filter_ql) == 0:
                filter_ql = f' WHERE {k}'
            else:
                filter_ql += f' AND {k} '
            if v is not None:
                filter_ql += '=%s'
                args = *args, v
            else:
                filter_ql += ' IS NULL '

        filter_ql += ' ORDER BY id DESC '

        if limit is not None:
            if not isinstance(limit, int):
                raise RuntimeError(f'Invalid limit type: "{type(limit)}"')
            filter_ql += f' LIMIT {limit}'

        res = []

        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT id, '
                            '       start_at, '
                            '       end_at, '
                            '       price, '
                            '       issuer_id, '
                            '       executor_id, '
                            '       transfer_addr, '
                            '       is_started, '
                            '       is_finished '
                            'FROM walk_requests '
                            f'{filter_ql};', args)
                for i in cur:
                    (_id,
                     start_at,
                     end_at,
                     price,
                     issuer_id,
                     executor_id,
                     transfer_addr,
                     is_started,
                     is_finished) = i
                    if isinstance(start_at, int):
                        start_at = datetime.datetime.fromtimestamp(start_at)
                    elif isinstance(start_at, str):
                        start_at = dateparser.parse(start_at)

                    if isinstance(end_at, int):
                        end_at = datetime.datetime.fromtimestamp(end_at)
                    elif isinstance(end_at, str):
                        end_at = dateparser.parse(end_at)

                    dogs = []

                    with db_conn() as db:
                        with db.cursor() as cur:
                            cur.execute('SELECT dog_id '
                                        'FROM walk_request_dogs ' 
                                        'WHERE request_id=%s;', (_id,))
                            for dog_id, in cur:
                                dogs.append(Dog.fetch(id=dog_id))

                    zones = []
                    with db_conn() as db:
                        with db.cursor() as cur:
                            cur.execute('SELECT zone_id '
                                        'FROM walk_request_zones '
                                        'WHERE request_id=%s;', (_id,))
                            for zone_id, in cur:
                                zones.append(WalkZone.fetch(id=zone_id))

                    issuer = User.fetch(id=issuer_id)
                    executor = User.fetch(id=executor_id)

                    res.append(WalkRequest(_id,
                                           start_at,
                                           end_at,
                                           price,
                                           issuer,
                                           executor,
                                           transfer_addr,
                                           is_started,
                                           is_finished,
                                           dogs,
                                           zones))

        return res

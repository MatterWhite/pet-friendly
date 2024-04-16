from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List

from db import db_conn
from models.walk_zone import WalkZone


@dataclass(frozen=True)
class Dog:
    _id: int
    owner_id: int
    name: str
    height: Optional[str] = None
    weight: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    favourite_zones: List[WalkZone] = field(default_factory=list)

    @staticmethod
    def fetch(**kvargs) -> Optional[Dog]:
        key, value = list(kvargs.items())[0]
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT id, '
                            '       owner_id, '
                            '       name, '
                            '       height, '
                            '       weight, '
                            '       breed, '
                            '       color '
                            'FROM dogs '
                            f'WHERE {key}=%s '
                            'LIMIT 1;', (value,))
                res = cur.fetchone()
        if res is None:
            return None

        (_id,
         owner_id,
         name,
         height,
         weight,
         breed,
         color,) = res

        favor_zones = []
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT zone_id '
                            'FROM dog_favor_zones '
                            'WHERE dog_id=%s;', (_id,))
                for zone_id, in cur:
                    favor_zones.append(WalkZone.fetch(id=zone_id))

        return Dog(*res, favor_zones)

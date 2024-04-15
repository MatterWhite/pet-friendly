from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from db import db_conn


@dataclass(frozen=True)
class UserType:
    _id: int
    name: str

    @staticmethod
    def fetch(with_wallet: bool = False, **kvargs) -> Optional[UserType]:
        key, value = list(kvargs.items())[0]
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT id, name '
                            'FROM user_types '
                            f'WHERE {key}=%s '
                            'LIMIT 1;', (value,))
                res = cur.fetchone()
        if res is None:
            return None
        return UserType(*res)

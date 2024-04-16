from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from db import db_conn


@dataclass(frozen=True)
class WalkZone:
    _id: int
    name: str
    district: str
    description: str
    square: str
    has_special_equipment: bool

    @staticmethod
    def fetch(**kvargs) -> Optional[WalkZone]:
        key, value = list(kvargs.items())[0]
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT id, '
                            '       name, '
                            '       district, '
                            '       description, '
                            '       square, '
                            '       has_special_equipment '
                            'FROM walk_zones '
                            f'WHERE {key}=%s '
                            'LIMIT 1;', (value,))
                res = cur.fetchone()
                return WalkZone(*res) if res is not None else None

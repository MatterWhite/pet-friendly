from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional

from db import db_conn


@dataclass(frozen=True)
class Wallet:
    owner_id: int
    balance_real: int
    balance_freezed: int
    wallet_freezed: bool
    created_at: datetime
    updated_at: datetime

    def deposit(self, amount: int):
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('UPDATE wallets '
                            'SET balance_real=balance_real+%s '
                            'WHERE owner_id=%s;', (amount, self.owner_id))
            db.commit()

    def withdraw(self, amount: int):
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('UPDATE wallets '
                            'SET balance_real=balance_real+%s '
                            'WHERE owner_id=%s;', (-amount, self.owner_id))
            db.commit()

    @staticmethod
    def fetch(**kvargs) -> Optional[Wallet]:
        key, value = list(kvargs.items())[0]
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT owner_id, '
                            '       balance_real, '
                            '       balance_freezed, '
                            '       wallet_freezed, '
                            '       created_at, '
                            '       updated_at '
                            'FROM wallets '
                            f'WHERE {key}=%s '
                            'LIMIT 1;', (value,))
                res = cur.fetchone()
                return Wallet(*res) if res is not None else None

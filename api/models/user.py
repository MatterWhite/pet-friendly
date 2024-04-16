from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from db import db_conn
from models.user_type import UserType
from models.wallet import Wallet


@dataclass
class User:
    _id: int
    name: str
    email: str
    password: str
    phone: str
    bio: str
    user_type: UserType
    wallet: Optional[Wallet] = None

    @staticmethod
    def fetch(with_wallet: bool = False, **kvargs) -> Optional[User]:
        key, value = list(kvargs.items())[0]
        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT users.id, '
                            '       username, '
                            '       email, '
                            '       password, '
                            '       phone, '
                            '       bio, '
                            '       user_types.id, '
                            '       user_types.name '
                            'FROM users '
                            'JOIN user_types '
                            '   ON user_types.id=users.user_type '
                            f'WHERE users.{key}=%s '
                            'LIMIT 1;', (value,))
                res = cur.fetchone()
        if res is None:
            return
        wallet = None
        if with_wallet:
            wallet = Wallet.fetch(owner_id=res[0])
        user_type = UserType(*res[-2:])
        return User(*res[:-2], user_type, wallet)

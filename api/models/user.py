from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from db import db_conn
from models.user_type import UserType


@dataclass
class User:
    _id: int
    name: str
    email: str
    password: str
    phone: str
    bio: str
    user_type: UserType

    @staticmethod
    def fetch(**kvargs) -> Optional[User]:
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
        user_type = UserType(*res[-2:])
        return User(*res[:-2], user_type)

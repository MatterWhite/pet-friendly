from dataclasses import dataclass

import psycopg2.errors

from db import db_conn
from models.user import User
from models.user_type import UserType


@dataclass(frozen=True)
class RegisterUserModel:
    name: str
    email: str
    pasword: str
    phone: str
    bio: str
    user_type: str

    def save(self) -> User:
        try:
            user_type = UserType.fetch(name=self.user_type)
            with db_conn() as db:
                with db.cursor() as cur:
                    cur.execute('INSERT INTO users '
                                '(username, email, password, phone, bio, user_type) '
                                'VALUES (%s, %s, %s, %s, %s, %s) '
                                'RETURNING id;', (self.name, self.email, self.pasword, self.phone, self.bio, user_type._id))
                    user_id, = cur.fetchone()
                db.commit()
            return User.fetch(id=user_id, with_wallet=True)
        except psycopg2.errors.UniqueViolation as e:
            raise ValueError('Duplicate creds!')

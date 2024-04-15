from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Type

import aiohttp
import aiohttp.web_request
from aiohttp import web_request

from db import db_conn
from models.user import User
from models.user_type import UserType


# from models.employee import Employee


class NotAuthorizedError(Exception):
    pass


class AuthorizedUser(User):

    def __init__(self, request: aiohttp.web_request.Request):
        if request.headers.get('Authorization') is None:
            raise ValueError('Header \'Authorization\' must be provided')
        token = request.headers['Authorization']
        email, hss = token.split(',')

        with db_conn() as db:
            with db.cursor() as cur:
                cur.execute('SELECT users.id '
                            'FROM users '
                            'WHERE ENCODE(SHA512(CONCAT(users.email, users.password)::bytea), \'HEX\')=%s '
                            'AND email=%s '
                            'LIMIT 1;', (hss, email))
                u_id, = cur.fetchone()

        user = User.fetch(id=u_id, with_wallet=True)

        self._id = user._id
        self.name = user.name
        self.email = user.email
        self.password = user.password
        self.phone = user.phone
        self.bio = user.bio
        self.user_type = user.user_type
        self.wallet = user.wallet


class IssuerUser(AuthorizedUser):
    def __init__(self, request: aiohttp.web_request.Request):
        super().__init__(request)
        if self.user_type.name != 'Заказчик':
            raise NotAuthorizedError()


class ExecutorUser(AuthorizedUser):
    def __init__(self, request: aiohttp.web_request.Request):
        super().__init__(request)
        if self.user_type.name != 'Исполнитель':
            raise NotAuthorizedError()

from typing import Optional

import aiohttp
import aiohttp.web
import aiohttp.web_request
import psycopg2.errors

from auth import AuthorizedUser
from models.reg_user import RegisterUserModel
from models.user import User
from router import routes

from .walkzones import *
from .walk_requests import *
from .wallet import *


@routes.post('/register')
async def post_register(request: aiohttp.web_request.Request, user_info: RegisterUserModel) -> User:
    return user_info.save()


@routes.get('/user')
async def user_info(request: aiohttp.web_request.Request, user: AuthorizedUser) -> User:
    return user

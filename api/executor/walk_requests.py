from typing import List

from auth import ExecutorUser, NotAuthorizedError
from models.walk_request import WalkRequest
from router import routes
import aiohttp.web_request


@routes.post('/walk_requests/assign')
async def assign_walk_request(request: aiohttp.web_request.Request, user: ExecutorUser, walk_request_id: int) -> None:
    walk = WalkRequest.fetch_one(id=walk_request_id)
    walk.assign_executor(user._id)


@routes.post('/walk_requests/begin')
async def begin_walk_request(request: aiohttp.web_request.Request, user: ExecutorUser, walk_request_id: int) -> None:
    walk = WalkRequest.fetch_one(id=walk_request_id)
    if walk.executor._id != user._id:
        raise NotAuthorizedError()
    walk.begin()


@routes.post('/walk_requests/finish')
async def finish_walk_request(request: aiohttp.web_request.Request, user: ExecutorUser, walk_request_id: int) -> None:
    walk = WalkRequest.fetch_one(id=walk_request_id)
    if walk.executor._id != user._id:
        raise NotAuthorizedError()
    walk.finish()

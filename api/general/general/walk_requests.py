from typing import List, Union, Optional

from auth import AuthorizedUser, NotAuthorizedError, IssuerUser, ExecutorUser
from models.walk_request import WalkRequest
from router import routes
import aiohttp.web_request


@routes.post('/walk_requests/assign_walk_zones')
async def assign_walk_zone_request(request: aiohttp.web_request.Request,
                                   user: AuthorizedUser,
                                   walk_request_id: int,
                                   zone_ids: List[int]) -> WalkRequest:
    walk = WalkRequest.fetch(id=walk_request_id)
    if (user.user_type.name == 'Заказчик' and walk.issuer._id == user._id) \
            or (user.user_type.name == 'Исполнитель' and walk.executor_id != user._id):
        raise NotAuthorizedError()

    if walk.is_started:
        raise ValueError('Already started')

    walk.assign_zones(zone_ids)
    return WalkRequest.fetch_one(id=walk_request_id)


@routes.get('/walk_requests/free')
async def get_free_walk_requests(request: aiohttp.web_request.Request,
                                 user: Union[IssuerUser, ExecutorUser]) -> List[WalkRequest]:
    return WalkRequest.fetch_many(limit=100, executor_id=None)


@routes.get('/walk_requests')
async def get_walk_requests(request: aiohttp.web_request.Request,
                            user: Union[IssuerUser, ExecutorUser],
                            is_started: Optional[bool] = None,
                            is_finished: Optional[bool] = None) -> List[WalkRequest]:
    ret_ids = []

    filter_args = {
    }
    if is_started is not None:
        filter_args['is_started'] = is_started
    if is_finished is not None:
        filter_args['is_finished'] = is_finished

    if isinstance(user, IssuerUser):
        filter_args['issuer_id'] = user._id
    else:
        filter_args['executor_id'] = user._id

    return WalkRequest.fetch_many(**filter_args)

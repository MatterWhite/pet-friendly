import aiohttp.web_request

from auth import IssuerUser
from models.create_request import CreateWalkRequestModel
from models.walk_request import WalkRequest
from router import routes


@routes.post('/walk_requests/new')
async def post_walk_request(request: aiohttp.web_request.Request, walk: CreateWalkRequestModel,
                            user: IssuerUser) -> WalkRequest:
    return walk.save(user._id)

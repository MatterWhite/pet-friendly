from typing import List

from auth import AuthorizedUser
from db import db_conn
from models.walk_zone import WalkZone
from router import routes
import aiohttp.web_request


@routes.get('/walkzones')
async def get_walkzones(request: aiohttp.web_request.Request, user: AuthorizedUser) -> List[WalkZone]:
    ret = []
    with db_conn() as db:
        with db.cursor() as cur:
            cur.execute('SELECT id, name, district, description, square, has_special_equipment '
                        'FROM walk_zones;')
            for c in cur:
                ret.append(WalkZone(*c))
    return ret

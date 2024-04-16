from typing import List

from auth import AuthorizedUser, IssuerUser
from db import db_conn
from models.dog import Dog
from models.reg_dog import RegisterDogModel
from router import routes
import aiohttp.web_request


@routes.post('/dogs/new')
async def post_new_dog(request: aiohttp.web_request.Request, dog: RegisterDogModel, user: IssuerUser) -> Dog:
    return dog.save(user._id)


@routes.post('/dogs/assign_favor_walkzone')
async def post_assign_dog_favor_walkzone(request: aiohttp.web_request.Request, user: IssuerUser, dog_id: int,
                                         zone_ids: List[int]) -> Dog:
    dog = Dog.fetch(id=dog_id)
    if dog.owner_id != user._id:
        raise ValueError('not dog owner')
    with db_conn() as db:
        with db.cursor() as cur:
            cur.execute('DELETE FROM dog_favor_zones WHERE dog_id=%s;', (dog_id,))
            for zone_id in zone_ids:
                cur.execute('INSERT INTO dog_favor_zones (dog_id, zone_id) VALUES (%s, %s);', (dog_id, zone_id))
        db.commit()
    return Dog.fetch(id=dog_id)


@routes.get('/dogs')
async def get_dogs(request: aiohttp.web_request.Request, user: IssuerUser) -> List[Dog]:
    ret_ids = []
    with db_conn() as db:
        with db.cursor() as cur:
            cur.execute('SELECT id '
                        'FROM dogs '
                        'WHERE owner_id=%s;', (user._id,))
            ret_ids = cur.fetchall()
    ret = []
    for _id, in ret_ids:
        ret.append(Dog.fetch(id=_id))
    return ret

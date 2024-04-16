import logging

from mw import middleware

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

from aiohttp import web

from router import routes

from general import *

from issuer import *

if __name__ == '__main__':
    app = web.Application()
    api = web.Application(middlewares=[middleware])
    api.router.add_routes(routes)
    app.add_subapp('/api', api)
    web.run_app(app, port=8081)

from __future__ import annotations
import datetime
import inspect
import typing

import ujson
import logging
import time
import traceback
from typing import Optional

import aiohttp
import aiohttp.web
import aiohttp.web_request
import aiohttp.web_exceptions
import psycopg2
import psycopg2.errors
from aiohttp import web

import type_unpack

log = logging.getLogger()


# def main_middleware(handler):
#     async def wrapper(request: aiohttp.web_request.Request):

@web.middleware
async def middleware(request: aiohttp.web_request.Request, handler):
    def serialize(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime) or isinstance(obj, datetime.time):
            serial = obj.isoformat()
            return serial

        ret = obj.__dict__
        if '_id' in ret:
            ret['id'] = ret['_id']
            del (ret['_id'])
        return ret

    error = None
    status = 200
    resp: Optional[dict] = None
    try:
        try:
            handler_spec = inspect.getfullargspec(handler)

            kvargs = {}
            for k in request.query.keys():
                if k in handler_spec.args:
                    kvargs[k] = request.query[k]
            for k in request.match_info.keys():
                if k in handler_spec.args:
                    kvargs[k] = request.match_info[k]
            if request.body_exists:
                reader = await request.json()
                if reader is not None:
                    for k in reader.keys():
                        if k not in kvargs:
                            if k in handler_spec.args:
                                kvargs[k] = reader[k]

            real_kvargs = {}
            required_args = list(
                filter(lambda x: not isinstance(x, aiohttp.web_request.Request),
                       handler_spec.annotations))

            type_errors = ''

            for k, v in kvargs.items():
                if handler_spec.annotations.get(k) is not None:
                    arg_annot = handler_spec.annotations[k]

                    real_kvargs[k], err = type_unpack.unpack_from_annotation(v, arg_annot)

                    if len(err) > 0:
                        if len(type_errors) > 0:
                            type_errors += '\n'
                        type_errors += err
                else:
                    real_kvargs[k] = v

            if len(type_errors) > 0:
                raise ValueError(type_errors + '\n' + str(kvargs))

            resp = await handler(request, **real_kvargs)
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            raise e
    except psycopg2.errors.CheckViolation as cve:
        error = str(cve).split('\n')[0]
        status = 400
    except ujson.JSONDecodeError as je:
        error = str(je)
        status = 400
    except TypeError as te:
        if 'required positional argument' in str(te):
            error = f'Missing arguments: {str(te).split(": ")[-1]}'
        else:
            error = 'type error'
        status = 400
    except KeyError as ke:
        error = f'key not found: {ke}'
        status = 400
    except ValueError as ve:
        error = str(ve)
        status = 400
    except aiohttp.web_exceptions.HTTPMethodNotAllowed as e:
        error = 'method not allowed'
        status = e.status
    except aiohttp.web_exceptions.HTTPNotFound as e:
        error = 'not found'
        status = e.status
    except aiohttp.web_exceptions.HTTPClientError as ce:
        error = str(ce)
        status = ce.status
    except Exception as e:
        log.critical(f'Unexpected: {e}')
        error = 'internal'
        status = 500
    finally:
        if error is not None:
            error = error.replace('"', '\'')
            end = time.perf_counter_ns()
            return web.json_response({
                'status': 'err',
                'error': error
            },
                status=status, dumps=lambda x: ujson.dumps(x, default=serialize, indent=4))

    return web.json_response({
        'status': 'ok',
        'payload': resp
    },
        status=200, dumps=lambda x: ujson.dumps(x, default=serialize, indent=4))
    # return wrapper

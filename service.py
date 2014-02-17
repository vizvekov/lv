# coding: utf8
import json

from functools import wraps
from bottle import Bottle, run, request, response, abort
from classes.CloudVM import CloudVM

api = Bottle()
cloud_vm = CloudVM()

# API Design
# JSON для всего
#
# /v0 версия API
# /v0/nodes POST - создать ноду
#           GET - прочитать параметры всех нод в виде списка
# /v0/nodes/<node_id>
#           GET - JSON информация о ноде
#           PUT - изменить у существующей ноды параметры


def common_headers(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        response.set_header('Content-Language', 'en')
        response.content_type = 'application/json'
        return function(*args, **kwargs)
    return wrapper


@api.post('/v0/nodes')
@common_headers
def add_node():
    response.status = 201

    host_name = request.forms.get('host_name')
    user_name = request.forms.get('user_name')
    password = request.forms.get('password')

    # Validate
    if not host_name:
        abort(400, 'Host name not specified')
    if not user_name:
        abort(400, 'User name not specified')
    if not password:
        abort(400, 'Password not specified')

    # Delegate
    cloud_vm.add_node(host_name, user_name, password)

    # TODO: We have to return JSON describing the node
    return {'host_name': host_name, 'user_name': user_name}


@api.get('/v0/nodes')
@common_headers
def get_nodes():
    response.status = 200
    return json.dumps([{'host_name': '10.0.0.1', 'user_name': 'aza'},
                       {'host_name': '10.0.0.2', 'user_name': 'aka'},
                       {'host_name': '10.0.0.3', 'user_name': 'aba'}])


if __name__ == '__main__':
    run(api, host='107.170.17.199', port=8080)


# coding: utf8
import json

from functools import wraps
from bottle import Bottle, run, request, response, abort
from classes.CloudVM import CloudVM

api = Bottle()
cloud_vm = CloudVM()

node_name = ""

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


@api.post('/v0/vms_del')
@common_headers
def process_node():
    response.status = 200
    vm_name = request.forms.post('vm_name')
    if not vm_name:
        abort(400,"No vm name")

    cloud_vm.undefine_vm(vm_name)

@api.post('/v0/vms')
@common_headers
def add_vm():
    response.status = 200
    vm_name = request.forms.post('name')
    if not vm_name:
        abort(400,'VM name not specified')

    ram = request.forms.post('ram')
    if not ram:
        abort(400,'VM ram not specified')

    ncpu = request.forms.post('ncpu')
    if not ncpu:
        abort(400,'VM cpu num not specified')

    disk_size = request.forms.post('disk_size')
    if not disk_size:
        abort(400,'VM disk size not specified')

    if not cloud_vm.create_vm(vm_name,1024,1,node_name):
        abort(400, "VM is not created")
    cloud_vm.add_disk(vm_name,"/root/IMAGES/ubuntu_image.qcow2","50")
    cloud_vm.add_interface(vm_name)
    try:
        cloud_vm.define_vm(vm_name)
        cloud_vm.start_vm(vm_name)
    except Exception, e:
        abort(400,e)
    if cloud_vm.get_vm_stat(vm_name):
        return {'vm_name': vm_name, 'status': 'Running', 'node': node_name}
    else:
        abort(400,"VM is not started")


@api.get('/v0/vms')
@common_headers
def get_vms():
    response.status = 200
    return json.dumps(cloud_vm.get_vms())


@api.post('/v0/subnet')
@common_headers
def add_subnet():
    response.status = 201
    subnet = request.forms.post('subnet')
    try:
        cloud_vm.add_subnet(subnet)
        return {'status': True}
    except Exception, e:
        return {'status': False, 'error': e}


@api.get('/v0/subnet')
@common_headers
def get_subnets():
    response.status = 201
    return {'subnets': cloud_vm.get_subnets()}


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
    node_name = cloud_vm.add_node(host_name, user_name, password)

    if cloud_vm.get_node_status(node_name):
        status = "Redy"
    else:
        status = "Error"

    # TODO: We have to return JSON describing the node
    return {'host_name': node_name, 'status': status}


@api.get('/v0/nodes')
@common_headers
def get_nodes():
    response.status = 200
    return json.dumps(cloud_vm.get_nodes())


if __name__ == '__main__':
    run(api, host='107.170.17.199', port=8080)


from flask import jsonify, request
import json
import logging
import os
import pathlib
import re
import yaml

import catalog
import comp
from maestro import app

log = logging.getLogger(__name__)

s = {}
w = ''

@app.route('/service', methods=['GET'])
def get_services():
    return json.dumps(s)

@app.route('/service', methods=['POST'])
def post_service():
    service = install(request.json)
    return json.dumps(service)

@app.route('/service/<service>', methods=['DELETE'])
def delete_service(service):
    removed_service = remove(service)
    return json.dumps(removed_service)


def load(workdir):
    global s
    global w
    w = workdir

    if(pathlib.Path(workdir + '/services/services.yml').is_file()):
        with open(w + "/services/services.yml", "rb") as file:
            s = yaml.load(file.read())
            if(s is None):
                s = {}

    if(not 'services' in s):
        s['services'] = {}


def save():
    with open(w + "/services/services.yml", "w") as file:
        file.write(yaml.dump(s))

def update():
    log.debug('Update')
    toUpgrade = []
    for name in s['services']:
        comp.pull(w, s['services'][name])
        if(comp.checkImage(w, s['services'][name])):
            toUpgrade.append(s['services'][name])
    for service in toUpgrade:
        upgrade(service)

def upgrade(service):
    log.info('Upgrade service %s', service['name'])

    updater = catalog.getUpdater(service['name'])

    if updater is None:
        comp.up(w, service)
        return

    if not updater in s['services']:
        install({'name': updater, 'params': {}})
        return

    comp.pull(w, s['services'][updater])
    comp.up(w, s['services'][updater])


def restart(service_name):
    service = s['services'][service_name]

    comp.down(w, service, False, False)
    comp.up(w, service)


def install(service):
    log.info('Install service %s', service['name'])

    for dep in catalog.getDepends(service['name']):
        if not dep in s['services']:
            log.info('Depends on %s', dep)
            install({'name': dep, 'params': {}})

    configure(service)

    s['services'][service['name']] = service
    save()

    comp.up(w, service)

    return service


def configure(service):
    sha = catalog.getComposeSha(service['name'])

    compose = catalog.getComposeFile(service['name'])

    writeCompose(service, compose)

def writeCompose(service, compose):
    r = re.compile('{{([^}]*)}}')

    params = r.findall(compose)

    for param in params:
        val = getParamValue(service, param)
        compose = compose.replace('{{' + param + '}}', val)

    if(not pathlib.Path(w + "/services/" + service['name']).is_dir()):
        pathlib.Path(w + "/services/" + service['name']).mkdir(parents=True)

    with open(w + "/services/" + service['name'] + "/docker-compose.yml", "w") as file:
        file.write(compose)

def computeParams(service, params):
    result = {}

    catalogParams = catalog.getServiceParams(service['name'])
    for p in catalogParams:
        v = getParamValue(service, p)
        result[p] = v

    return result

def getParamValue(service, param):
    if 'params' in service and param in service['params']:
        return service['params'][param]

    if param in os.environ:
        return os.environ[param]

    val, founded = catalog.getServiceParam(service['name'], param)
    if founded:
        return val

    raise AssertionError("Undefined required param value for '%s'", param)

def remove(service_name):
    service = s['services'].pop(service_name, None)

    comp.down(w, service, True, True)

    save()
    return service

def install_required():
    for service in catalog.getRequiredServices():
        if not service in s['services']:
            install({'name': service, 'params': {}})

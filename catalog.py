import hashlib
import pathlib
import yaml

w = ""
c = {}

def load(workdir):
    global c
    global w

    w = workdir

    with open(w + "/catalog/catalog.yml", "rb") as file:
        c = yaml.load(file.read())

    return c

def getComposeSha(name):

    with open(w + "/catalog/" + name + "/docker-compose.yml", "rb") as file:
        compose = file.read()

    return hashlib.sha256(compose).hexdigest()

def getDepends(name):
    if name in c['services'] and 'depends' in c['services'][name]:
        return c['services'][name]['depends']
    return []

def getComposeFile(name):

    with open(w + "/catalog/" + name + "/docker-compose.yml", "r") as file:
        compose = file.read()
    return compose

def getServiceParams(name):
    if name in c['services'] and 'params' in c['services'][name]:
        return c['services'][name]['params']
    return {}

def getServiceParam(name, param):

    if name in c['services'] and 'params' in c['services'][name] and param in c['services'][name]['params']:
        p = c['services'][name]['params'][param]
        if p['required'] and p['default'] == "":
            return ("", False)
        return (p['default'], True)

    return ("", False)

def getUpdater(name):
    if name in c['services'] and 'updater' in c['services'][name]:
        return c['services'][name]['updater']
    return None

def getRequiredServices():
    required = []

    for service in c['services']:
        if 'required' in c['services'][service] and c['services'][service]['required']:
            required.append(service)

    return required

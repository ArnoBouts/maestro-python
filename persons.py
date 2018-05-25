from flask import jsonify, request
import json
import ldap
import os

from maestro import app

@app.route('/person', methods=['GET'])
def get_persons():
    return json.dumps(getList())

@app.route('/person', methods=['POST'])
def post_person():
    add(request.json)

@app.route('/person/<cn>', methods=['DELETE'])
def delete_person(cn):
    delete(cn)

@app.route('/person/<cn>/service/<service>', methods=['PATCH'])
def allow_service(cn, service):
    grantService(cn, service, request.json['allow'])

def getList():

    result = []

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    rs = l.search_s("ou=people,dc=home", ldap.SCOPE_SUBTREE, "(&(objectClass=person))", ['dn', 'cn', 'sn', 'mail', 'gidNumber', 'uidNumber'])

    for r in rs:
        p = {}
        p['dn'] = r[0]
        if 'cn' in r[1]:
            p['cn'] = r[1]['cn'][0].decode('utf-8')
        if 'sn' in r[1]:
            p['sn'] = r[1]['sn'][0].decode('utf-8')
        if 'mail' in r[1]:
            p['mail'] = r[1]['mail'][0].decode('utf-8')
        if 'gidNumber' in r[1]:
            p['gidNumber'] = int(r[1]['gidNumber'][0].decode('utf-8'))
        if 'uidNumber' in r[1]:
            p['uidNumber'] = int(r[1]['uidNumber'][0].decode('utf-8'))
        result.append(p)

    l.unbind_s()

    return result


def add(p):

    dn = 'cn={},ou=people,dc=home'.format(p['cn'])

    cn = p['cn'].encode('utf-8')
    sn = p['sn'].encode('utf-8')
    mail = p['mail'].encode('utf-8')
    gidNumber = str(p['gidNumber']).encode('utf-8')
    uidNumber = str(p['uidNumber']).encode('utf-8')

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    ldif = [
        ('objectclass', [b'top', b'person', b'organizationalPerson', b'inetOrgPerson', b'posixAccount']),
        ('cn', cn),
        ('sn', sn),
        ('uid', cn),
        ('mail', mail),
        ('homeDirectory', b''),
        ('gidNumber', gidNumber),
        ('uidNumber', uidNumber)
    ]

    l.add_s(dn, ldif)
    
    l.unbind_s()


def delete(name):
    dn = 'cn={},ou=people,dc=home'.format(name)

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    l.delete_s(dn)

    l.unbind_s()


def edit(p):

    dn = 'cn={},ou=people,dc=home'.format(p['cn'])
    
    cn = p['cn'].encode('utf-8')
    sn = p['sn'].encode('utf-8')
    mail = p['mail'].encode('utf-8')
    gidNumber = str(p['gidNumber']).encode('utf-8')
    uidNumber = str(p['uidNumber']).encode('utf-8')

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    ldif = [
        (ldap.MOD_REPLACE, 'sn', sn),
        (ldap.MOD_REPLACE, 'uid', cn),
        (ldap.MOD_REPLACE, 'mail', mail),
        (ldap.MOD_REPLACE, 'homeDirectory', b''),
        (ldap.MOD_REPLACE, 'gidNumber', gidNumber),
        (ldap.MOD_REPLACE, 'uidNumber', uidNumber)
    ]

    l.modify_s(dn, ldif)

    l.unbind_s()

def grantService(person, service, allow):

    personDn = 'cn={},ou=people,dc=home'.format(person).encode('utf-8')
    serviceDn = 'cn={},ou=groups,dc=home'.format(service)
    
    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    ldif = []
    if allow:
        ldif = [(ldap.MOD_ADD, 'uniqueMember', personDn)]
    else:
        ldif = [(ldap.MOD_DELETE, 'uniqueMember', personDn)]

    l.modify_s(serviceDn, ldif)

    l.unbind_s()

from flask import jsonify, request
import ldap
import ldap.modlist as modlist
import os

from maestro import app

@app.route('/group')
def get():
    return jsonify(getList())

@app.route('/group', methods=['POST'])
def post():
    add(request.json)

@app.route('/group/<cn>', methods=['DELETE'])
def delete_group(cn):
    delete(cn)

def getList():
    result = []

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    rs = l.search_s("ou=groups,dc=home", ldap.SCOPE_SUBTREE, "(&(objectClass=groupOfUniqueNames))", ['dn', 'cn', 'uniqueMember'])

    for r in rs:
        g = {}
        g['dn'] = r[0]
        if 'cn' in r[1]:
            g['cn'] = r[1]['cn'][0].decode('utf-8')
        if 'uniqueMember' in r[1]:
            g['uniqueMembers'] = []
            for m in r[1]['uniqueMember']:
                g['uniqueMembers'].append(m.decode('utf-8'))
        result.append(g)

    l.unbind_s()

    return result


def add(g):

    cn = g['name'].encode('utf-8')
    dn = 'cn={},ou=groups,dc=home'.format(g['name'])

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    ldif = [
        ('objectclass', [b'top', b'groupOfUniqueNames']),
        ('cn', cn),
        ('uniqueMember', b'')
    ]

    l.add_s(dn, ldif)

    l.unbind_s()


def delete(name):

    dn = 'cn={},ou=groups,dc=home'.format(name)

    l = ldap.initialize('ldap://{}:{}'.format(os.environ['LDAP_HOST'], os.environ['LDAP_PORT']))
    l.bind_s(os.environ['LDAP_ADMIN_DN'], os.environ['LDAP_ADMIN_PASSWORD'])

    l.delete_s(dn)

    l.unbind_s()

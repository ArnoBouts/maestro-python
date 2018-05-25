from flask import Flask
#from flask.ext.ldap import LDAP, login_required
import os

app = Flask(__name__)

app.config['LDAP_HOST'] = os.environ['LDAP_HOST'] if 'LDAP_HOST' in os.environ else 'ldap'
app.config['LDAP_DOMAIN'] = 'home'
app.config['LDAP_SEARCH_BASE'] = 'ou=people,dc=home'
app.config['LDAP_REQUIRED_GROUP'] = 'maestro'
app.config['LDAP_LOGIN_VIEW'] = 'login' 

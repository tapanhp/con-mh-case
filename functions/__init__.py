import os
import sys

sys.path.append('functions')
sys.path.append('pages')

import eventlet
from flask import Flask
from flask.ext.assets import Environment
import socket
from webassets.loaders import YAMLLoader

from flask.ext.mobility import Mobility

import environment
from functions.connect_to import getConnection

# MD Mar-2015 Doing tests with vcr needs plain old urllib2 to work, otherwise use the eventlet version for Celery tasks
if environment.equals('test') or not eventlet.patcher.already_patched:
    import urllib2
else:
    from eventlet.green import urllib2

# MD Oct-2015 OL-2112 Set a default timeout
socket.setdefaulttimeout(60)


def generate_mysql_uri(settings):
    return 'mysql+mysqlconnector://%s:%s@%s:%s/%s' % (
    settings['user'], settings['password'], settings['host'], settings['port'], settings['database'])

##############
# CREATE APP #
##############
app = Flask(__name__, template_folder="../templates")
Mobility(app)
app.secret_key = 'cauliflowers'
app.debug = False

###################
# UPLOAD SETTINGS #
###################
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 Mb limit
if environment.equals('production'):
    app.config['UPLOAD_FOLDER'] = '/media/uploads/'
else:
    app.config['UPLOAD_FOLDER'] = 'public/uploads/'

#####################
# DATABASE SETTINGS #
#####################
settings = getConnection('access')
app.config['SQLALCHEMY_DATABASE_URI'] = generate_mysql_uri(settings)
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 1000
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1500

app.config['SQLALCHEMY_BINDS'] = {
    'db1': app.config['SQLALCHEMY_DATABASE_URI'],
}

root_path = os.path.abspath("%s/.." % os.path.dirname(__file__))
tmp_path = "%s/tmp" % root_path

os.environ['BOTO_ENDPOINTS'] = os.path.abspath("%s/config/boto_endpoints.json" % root_path)

###################
# ASSETS SETTINGS #
###################
assets = Environment(app)
loader = YAMLLoader("%s/assets/assets.yml" % root_path)
bundles = loader.load_bundles()
assets.register(bundles)

assets.set_directory("%s/public" % root_path)
assets.load_path.append('./assets/')
assets.url = '/'
assets.manifest = "json:%s/public/gen/webassets-manifest.json" % root_path

development_mode = not environment.equals('production')
assets.cache = development_mode
assets.auto_build = development_mode
assets.debug = development_mode

# MD Feb-2015 Allow created files to be group writeable. This will fix some problems with files created in the /tmp
# directory that are accessed both by Celery and duesty scripts. The /tmp directory should have set "chmod g+s tmp"
os.umask(0o002)





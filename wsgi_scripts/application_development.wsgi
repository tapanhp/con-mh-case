import os, sys

this_dir = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(this_dir, '..'))
os.chdir(PROJECT_DIR)

virtualenv_path = os.path.expanduser('~/.virtualenvs/python2.7.8')

activate_this = os.path.join(virtualenv_path, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)

import environment
environment.set('development')

from app_main import app as application

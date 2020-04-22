
from flask.ext.testing import TestCase

import environment

environment.set('test')

from models import *
from app_main import app


class OhmTestCase(TestCase):
    def __init__(self, methodName):
        super(OhmTestCase, self).__init__(methodName)
        self.chuck = User.query.get(1)
        self.elvis = User.query.get(2)
        self.justin = User.query.get(3)

    def create_app(self):
        app.config['SECRET_KEY'] = 'sekrit!'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['PROPAGATE_EXCEPTIONS'] = True
        return app

    def tearDown(self):
        pass



import os

environment = os.environ.get('FLASK_ENVIRONMENT') or 'production'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# If limited db read-only operation desired during maintenance, set this to True
DB_READ_ONLY = False


def asimov_raw_table():
    if equals('test'):
        return 'asimov_raw_test'
    else:
        return 'asimov_raw'


def set(env):
    global environment
    environment = env

    from ohm_lib.config import config
    config(reset=True)


def get():
    return environment


def equals(env):
    return environment.lower() == env.lower()

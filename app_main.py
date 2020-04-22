import sys

from ohm_lib.config import config

sys.path.append('functions')
sys.path.append('pages')

import environment
import functools

from flask import jsonify, redirect, request, session, url_for
from flask.ext.login import LoginManager, current_user, AnonymousUserMixin
from functions import app
from models import User

login_manager = LoginManager()
login_manager.init_app(app)


# login_manager.session_protection = "strong"   # CBL - we should enable this but breaking tests

# MD Oct-2014 OL-94 This fixes problems where some templates may access current_user without a user being logged in
class OhmAnonymousUserMixin(AnonymousUserMixin):
    def __init__(self):
        super(OhmAnonymousUserMixin, self).__init__()
        self.user = None

    def short_name(self):
        return None

    def full_name(self):
        return None

    def hash(self):
        return None


login_manager.anonymous_user = OhmAnonymousUserMixin


def checkMobile(request):
    mobileQry = ''
    if hasattr(request, 'MOBILE') and request.MOBILE:
        mobileQry = "mobile/"

    return mobileQry


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def admin_login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated():
            if current_user.is_admin():
                return method(*args, **kwargs)
            else:
                return jsonify({'success': 0, 'msg': 'Not a valid user for this function'})
        else:
            set_passthrough(request.path)
            return redirect(url_for('login'))

    return wrapper

def set_passthrough(url):
    session['passthrough'] = url


def check_login_by_token(token):
    user_id = None
    if token:
        user_id = check_access_token(token)
    if user_id:
        return ohm_login(user_id=user_id)
    return None


def check_login_by_token_if_not_logged_in():
    token = request.args.get('access_token')
    if current_user.is_anonymous():
        check_login_by_token(token)
    return token


def check_access_token_login(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        check_login_by_token_if_not_logged_in()
        return method(*args, **kwargs)

    return wrapper


def login_required(method):
    def redirect_to_password(token):
        return redirect('/password/create?access_token=%s' % token)

    def redirect_to_signup(token=None):
        # If this is an ajax request, redirect doesn't help so just return a 401 with a json packet
        if request and request.is_xhr:
            data = {'status': -1, 'msg': 'Login required for Ajax call'}
            return jsonify(data), 401

        # MD Jul-2015 OL-1356 On the first time the mobile app starts up, send them to the mobile create_account page
        # so they can signup for OhmConnect. After that, send to the normal login page.
        if checkMobile(request) == 'mobile/' and not request.cookies.get('ohm_track_key'):
            return redirect_with_args('signup')
        else:
            page = 'login' if token else 'signup'  # if they look like they had a token send them to login
            if config().oem_equals('scp'):
                return redirect_with_args('login')
            elif 'shop' in request.path or 'store' in request.path:
                return redirect_with_args(page, store=True)
            else:
                return redirect_with_args(page)

    def dismiss_announcement():
        ann_id = request.args.get('ann_id')
        if ann_id:
            from models import Announcement
            ann = Announcement.query.get(ann_id)
            if ann:
                ann.dismiss(user=current_user)

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if session is None:
            ohm_logout()
            return redirect_to_signup()

        # Order of operations
        # 1. current session read from "session" cookie
        # 2. remember_token cookie
        # 3. access_token on query string
        token = check_login_by_token_if_not_logged_in()

        if current_user.is_authenticated():
            # prompt for setting password if they came in with an access token
            # OL-7886 Except for users that are unsubscribing since we don't want to put any other steps
            # in the way

            if current_user.is_deleted():
                ohm_logout()
                return redirect_to_signup()

            dismiss_announcement()

            if token and current_user.ohm_password_needed() and '/unsubscribe' not in request.path:
                session['passthrough'] = request.path
                return redirect_to_password(token)

            return method(*args, **kwargs)
        else:
            set_passthrough(request.path)
            return redirect_to_signup(token)

    return wrapper


def ohm_login(user_id=None, username=None, remember=True):
    logged_in_user = None

    if user_id is not None:
        logged_in_user = User.query.get(user_id)
    elif username is not None:
        logged_in_user = User.query.filter(User.username == username).first()

    # MD Jan-2015 Sometimes the session['username'] gets corrupted. Catch that here so we
    # can clear the session and redirect to the login page
    if not logged_in_user:
        return False

    return UserCredential.ohm_login(logged_in_user, remember=remember)


def ohm_logout():
    return UserCredential.ohm_logout()


# MD Jun-2015 MOB-1 The mobile app needs this to register the user for notifications
# MD Jun-2015 MAR-45 We also need to allow Ajax calls from the www site for page tracking
@app.after_request
def after_request(response):
    if response.headers.get('Access-Control-Allow-Origin') == None or response.headers.get('Access-Control-Allow-Origin') != 'https://shop.ohmconnect.com':
        response.headers.add('Access-Control-Allow-Origin', 'https://www.ohmconnect.com')

    if current_user.is_authenticated():
        response.headers.add('Current-User-Id', current_user.user_id)

    return response


def redirect_to_passthrough(url='/'):
    if 'passthrough' in session and session['passthrough'][0:5] != '/data' and \
            session['passthrough'][0:6] != '/popup' and \
            session['passthrough'][0:10] != '/dashboard':
        passthrough = session['passthrough']
        session.pop('passthrough', None)
        return redirect(passthrough)

    return redirect(url)



import pages.dashboard

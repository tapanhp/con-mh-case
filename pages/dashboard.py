from flask import jsonify, render_template, request, Response
from flask.ext.login import current_user, login_user

from functions import app
from models import User


@app.route('/dashboard', methods=['GET'])
def dashboard():

    login_user(User.query.get(1))

    args = {
            'gift_card_eligible': True,
            'cashout_ok': True,
            'user_below_silver': current_user.is_below_tier('Silver'),
    }
    return render_template("dashboard.html", **args)


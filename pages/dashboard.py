from flask import jsonify, render_template, request, Response
from flask.ext.login import current_user, login_user

from functions import app
from models import User, RelUserMulti
from models._helpers import db
from sqlalchemy import text

@app.route('/dashboard', methods=['GET'])
def dashboard():

    login_user(User.query.get(1))

    args = {
            'gift_card_eligible': True,
            'cashout_ok': True,
            'user_below_silver': current_user.is_below_tier('Silver'),
    }
    return render_template("dashboard.html", **args)

@app.route('/community', methods=['GET'])
def recent_users():

    login_user(User.query.get(1))
    sql = text("select dn, tier, balance, rel_user_multi.attribute from "
               "(select user.display_name as dn, user_id as uid, user.tier as tier,"
               " user.point_balance as balance from user ORDER BY user.signup_date DESC LIMIT 5)"
               " as recent_user left join rel_user_multi on recent_user.uid = rel_user_multi.user_id ")

    result = db.engine.execute(sql)
    users_data = []
    for row in result:
        ruser = {"display_name": row[0], "tier": row[1], "point_balance": row[2], "phone": row[3]}
        users_data.append(ruser)
    args = {
            'gift_card_eligible': True,
            'cashout_ok': True,
            'user_below_silver': current_user.is_below_tier('Silver'),
            'users': users_data
    }
    return render_template("recent_users.html", **args)
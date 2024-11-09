from flask import Blueprint, redirect, request, session, url_for
from controllers.authController import start_oauth_flow, get_oauth_tokens

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return start_oauth_flow()

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    credentials = get_oauth_tokens(code)
    return redirect(url_for('calendar.get_free_slots'))

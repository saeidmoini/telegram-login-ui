import os
from flask import request, jsonify, render_template, redirect, url_for, Blueprint, current_app
from .telegram_client import TelegramClientHandler  # Custom handler for Telegram client

login_bp = Blueprint('login', __name__)
login_bp.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
# Route for the home page
@login_bp.route('/')
def index():
    token = request.cookies.get('token')
    if token:
        handler = TelegramClientHandler(login_bp.secret_key, token=token)
        response = handler.login() if handler else {'logged_in': False}
        if response and response['logged_in']:
            return redirect(url_for(current_app.config.get('SUCCESS_URL', 'success')))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')

# Route for login
@login_bp.route('/login', methods=['POST'])
def login():
    api_id = request.form['api_id']
    api_hash = request.form['api_hash']
    phone = request.form['phone']
    handler = TelegramClientHandler(login_bp.secret_key, api_id=api_id, api_hash=api_hash, phone=phone)
    response = handler.login()
    return jsonify(response)

# Route for verifying the code sent to the phone
@login_bp.route('/verify_code', methods=['POST'])
def verify_code():
    code = request.form['code']
    token = request.cookies.get('token')
    handler = TelegramClientHandler(login_bp.secret_key, token=token)
    response = handler.verify_code(code)
    return jsonify(response)

# Route for verifying the password
@login_bp.route('/verify_password', methods=['POST'])
def verify_password():
    password = request.form['password']
    token = request.cookies.get('token')
    handler = TelegramClientHandler(login_bp.secret_key, token=token)
    response = handler.verify_password(password)
    return jsonify(response)

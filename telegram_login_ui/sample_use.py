from flask import Flask, render_template
from telegram_login_ui import login_bp
import os
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
# Configure the success URL after login
app.config['SUCCESS_URL'] = 'success'

# Register the login blueprint
app.register_blueprint(login_bp)

# Define the success page route
@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(debug=True)
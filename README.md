
---

# Telegram Login UI Package

This package provides a simple and efficient way to create a user interface for logging into Telegram accounts. It handles session management and authentication seamlessly, allowing you to use Telegram's API methods with either browser cookies or local sessions.

## Features

- **Blueprint Integration**: Easily integrate the login functionality into your Flask app using a blueprint.
- **Session Management**: Save phone numbers in local sessions and cookies for seamless API usage.
- **API Methods**: Use Telegram API methods with either cookies or sessions.
- **Duplicate Session Prevention**: Automatically disconnect and remove duplicate sessions.

---

## Installation

Install the package using `pip`:

```bash
pip install git+https://github.com/saeidmoini/telegram-login-ui
```

---

## Usage

### 1. Register the Login Blueprint

To integrate the login functionality, register the `login_bp` blueprint in your Flask app:

```python
from tg_login import login_bp

# Configure the success URL after login
app.config['SUCCESS_URL'] = 'example_success'

# Register the login blueprint
app.register_blueprint(login_bp)

# Define the success page route
@app.route('/example_success')
def example_success():
    return render_template('example_success.html')
```

---

### 2. Session Management

After logging in, the phone number is saved in the local session and a cookie in the browser. You can use these to interact with Telegram's API methods.

#### Using Cookies

To use the cookie for authentication:

```python
token = request.cookies.get('token')
args = {'token': token}
handler = TelegramClientHandler(app.secret_key, token=args['token'])
```

#### Using Local Sessions

To use the local session for background tasks:

```python
data = ['phone_number']
args = {'data': data}
handler = TelegramClientHandler(app.secret_key, data=args['data'])
```

---

### 3. Available Methods

#### `await handler.ensure_client_connected()`
Ensures the Telegram client is connected. If not, it attempts to connect.

#### `await handler.disconnect_remove()`
Disconnects the Telegram client and removes the session file to prevent duplicate sessions.

---

## Example

Here’s a complete example of how to use the package:

```python
from flask import Flask, request, render_template
from tg_login import login_bp
from tg_login import TelegramClientHandler

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the success URL
app.config['SUCCESS_URL'] = 'example_success'

# Register the login blueprint
app.register_blueprint(login_bp)

@app.route('/example_success')
def example_success():
    return render_template('example_success.html')

@app.route('/use_cookie')
async def use_cookie():
    token = request.cookies.get('token')
    handler = TelegramClientHandler(app.secret_key, token=token)
    await handler.ensure_client_connected()
    return "Connected using cookie!"

@app.route('/use_session')
async def use_session():
    phone_number = '+1234567890'
    handler = TelegramClientHandler(app.secret_key, data=[phone_number])
    await handler.ensure_client_connected()
    return "Connected using session!"
```


## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the package.

---

This documentation provides a clear overview of your package, its features, and how to use it effectively.
import jwt
from jwt import ExpiredSignatureError
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    SendCodeUnavailableError,
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError
)
import json
import shutil
import os
from .logger import logger
import asyncio
from dotenv import load_dotenv, set_key
from pathlib import Path

db_lock = asyncio.Lock()
class TelegramClientHandler:
    def __init__(self, SECRET_KEY, **kwargs):
        self.api_id = os.getenv('api_id')
        self.api_hash = os.getenv('api_hash')
        self.phone_code_hash = None
        self.client = None
        self.token = kwargs.get('token', False)
        self.data = kwargs.get('data', False)
        self.SECRET_KEY = SECRET_KEY
        self.new_session = False
        self.sessions_path = Path(os.getcwd(), "sessions")
        self.sessions_path.mkdir(parents=True, exist_ok=True)

        if self.data:
            self.phone = self.data[0]
            self.__session_pars()
        elif self.token:
            payload = jwt.decode(self.token, self.SECRET_KEY, algorithms=['HS256'])
            self.phone = payload['phone']
            self.__session_pars()
        else:
            self.phone = kwargs.get('phone')
            self.token = self.__generate_token()
        self.phone_code_hash = os.getenv(self.phone, None)
        try:
            loop = asyncio.new_event_loop()  # Create a new event loop
            asyncio.set_event_loop(loop)
            if self.new_session:
                self.client = TelegramClient(self.new_session, self.api_id, self.api_hash)
            else:
                self.new_session  = Path(self.sessions_path, self.phone)
                self.client = TelegramClient(self.new_session, self.api_id, self.api_hash)

        except Exception as e:
            logger.error(f"Telegram Cliend Starter : {e}")

    def save_to_env(self, key, value):
        try:
            env_path = Path.cwd() / '.env'

            if env_path.exists() and env_path.is_dir():
                raise IsADirectoryError(f"{env_path} is a directory, not a file.")

                # If the file doesn't exist, create it
            if not env_path.exists():
                env_path = Path.cwd() / '.env'
                # Ensure that .env is not a directory
                if env_path.is_dir():
                    raise IsADirectoryError(f"{env_path} is a directory, not a file.")
                env_path.touch(mode=0o600, exist_ok=True)

            # Save the key-value pair to the .env file
            set_key(dotenv_path=str(env_path), key_to_set=key, value_to_set=value)
            os.environ[key] = value

        except Exception as e:
            logger.error(f"Error saving to .env: {e}")
            raise

    async def ensure_client_connected(self):
        if self.client is not None and not self.client.is_connected():
            try:
                await self.client.connect()
                return True
            except Exception as e:
                logger.error(f"Error in client connectError in client connect: {e}")
        else:
            logger.error("Error in client connect. Client Didnt Worked")
            return False

    async def disconnect_remove(self):
        await self.client.disconnect()

        # Delete the session file
        session_file = f"{self.new_session}.session"
        if os.path.exists(session_file):
            os.remove(session_file)

    def __session_pars(self):
        try:
            session_file = os.path.join(self.sessions_path, f"{self.phone}.session")
            if os.path.exists(session_file):
                # جایگزین امن برای asyncio.run()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.new_session = loop.run_until_complete(self.__create_new_session())
                loop.close()
            else:
                logger.error('Session dosent exist')
                return None

        except ExpiredSignatureError:
            logger.error(f"Token for {self.phone} is expired.")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token for {self.phone}: {e}")
            raise

    async def __copy_session(self, new_session_name, base):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy, base, new_session_name)

    async def __create_new_session(self):
        session_number = 1  # Start from _2
        base = Path(self.sessions_path , self.phone + ".session")

        # Check if the file with the desired name already exists
        while os.path.exists(f"{self.sessions_path}/{self.phone}+{session_number}.session"):
            session_number += 1  # Increment the number until a unique name is found

        new_session_name = f"{self.sessions_path}/{self.phone}+{session_number}.session"

        await self.__copy_session(new_session_name, base)

        self.new_session = f"{self.sessions_path}/{self.phone}+{session_number}"

        return self.new_session

    async def __login_async(self):
        """Login or send a code if not authorized."""
        connect = await self.ensure_client_connected()
        if connect is False:
            return {'message': f'Please remove coockie .', 'logged_in': False}
        if await self.client.is_user_authorized():
            me = await self.client.get_me()
            await self.disconnect_remove()
            return {'message': f'Already logged in as {me.first_name}.', 'logged_in': True, 'token': self.token}

        code_request = await self.client.send_code_request(self.phone)
        phone_code_hash = code_request.phone_code_hash
        self.save_to_env(self.phone, phone_code_hash)
        await self.client.disconnect()
        return {'message': 'Code sent. Please check your phone.', 'logged_in': False, 'token': self.token}

    def login(self):
        """Wrapper for asynchronous login."""
        try:
            return asyncio.run(self.__login_async())
        except (SendCodeUnavailableError, FloodWaitError) as e:
            logger.error(f"Login error: {e}")
            return {'error': str(e)}, 400
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            return {'error': str(e)}, 500

    async def __verify_code_async(self, code):
        connect = await self.ensure_client_connected()
        if connect is False:
            return {'message': f'Please remove coockie .', 'logged_in': False}
        try:
            await self.client.sign_in(self.phone, code=code, phone_code_hash=self.phone_code_hash)
            me = await self.client.get_me()
            return {'message': f'Successfully signed in as {me.first_name}.', 'logged_in': True}
        except PhoneCodeExpiredError:
            print("The code has expired. Please request a new code.")
        except SessionPasswordNeededError:
            return {'error': 'Two-step verification is enabled. Please provide your password.', 'password_needed': True}
        except PhoneCodeInvalidError:
            return {'error': 'Invalid verification code. Please try again.'}
        finally:
            await self.disconnect_remove()

    def verify_code(self, code):
        try:
            response = asyncio.run(self.__verify_code_async(code))
            return response
        except Exception as e:
            logger.error(f"Error in verify_code: {e}")
            return {'error': str(e)}, 500

    async def __verify_password_async(self, password):
        connect = await self.ensure_client_connected()
        if connect is False:
            return {'message': f'Please remove coockie .', 'logged_in': False}
        try:
            await self.client.sign_in(password=password)
            me = await self.client.get_me()
            return {'message': f'Successfully signed in as {me.first_name}.', 'logged_in': True}
        except PasswordHashInvalidError:
            return {'error': 'Incorrect password. Please try again.'}
        finally:
            await self.disconnect_remove()

    def verify_password(self, password):
        try:
            response = asyncio.run(self.__verify_password_async(password))
            if 'error' in response:
                return {'error': response['error']}, 400
            return response
        except Exception as e:
            logger.error(f"Error in verify_password: {e}")
            return {'error': str(e)}, 500

    def __generate_token(self):
        """Generate a JWT for the authenticated user."""
        return jwt.encode({'phone': self.phone}, self.SECRET_KEY, algorithm='HS256')
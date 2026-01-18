import logging
import asyncio
from telethon import TelegramClient, errors
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeleAuth")

class TelegramAuth:
    def __init__(self, session_path: str):
        self.api_id = Config.TELEGRAM_API_ID
        self.api_hash = Config.TELEGRAM_API_HASH
        self.session_path = session_path
        self.client = None
        self.loop = None
        
        # Создаем цикл, чтобы Flask не ругался
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def _init_client(self):
        """Ленивая инициализация клиента"""
        if self.client is None:
            self.client = TelegramClient(
                self.session_path,
                self.api_id,
                self.api_hash,
                loop=self.loop
            )
        return self.client

    def connect(self):
        self._init_client()
        self.client.connect()

    def disconnect(self):
        try:
            if self.client:
                self.client.disconnect()
        except:
            pass

    def send_code(self, phone: str):
        """Отправка кода с запросом СМС"""
        self._init_client()
        self.connect()
        # force_sms=True просит Telegram отправить именно СМС
        return self.client.send_code_request(phone, force_sms=True)

    def sign_in(self, phone: str, code=None, password=None, phone_code_hash=None):
        """Вход"""
        self._init_client()
        self.connect()
        try:
            return self.client.sign_in(
                phone=phone,
                code=code,
                password=password,
                phone_code_hash=phone_code_hash
            )
        except errors.SessionPasswordNeededError:
            raise 
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            raise
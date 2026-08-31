import os
import json
import hmac
import hashlib
import requests
from http.server import BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
TWITCH_SECRET = os.environ.get('TWITCH_EVENTSUB_SECRET')

def send_telegram_message(text):
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(tg_url, data={"chat_id": TELEGRAM_CHANNEL_ID, "text": text})

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        msg_type = self.headers.get('Twitch-Eventsub-Message-Type')

        # 1. Ответ на рукопожатие Twitch (Challenge)
        if msg_type == 'webhook_callback_verification':
            data = json.loads(body)
            challenge = data.get('challenge')
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(challenge.encode('utf-8'))
            return

        # 2. Обработка события начала стрима
        if msg_type == 'notification':
            data = json.loads(body)
            event = data.get('event', {})
            broadcaster_name = event.get('broadcaster_user_name', 'Стример')
            
            msg = f"🔴 СТРИМ НАЧАЛСЯ!\n\nКанал {broadcaster_name} прямо сейчас в эфире!\n\nhttps://twitch.tv/{event.get('broadcaster_user_login')}"
            send_telegram_message(msg)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

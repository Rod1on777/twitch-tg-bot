import os
import requests
from http.server import BaseHTTPRequestHandler

TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')
TWITCH_CHANNEL = os.environ.get('TWITCH_CHANNEL')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')

def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    res = requests.post(url, data=data).json()
    return res.get('access_token')

def check_and_notify():
    token = get_twitch_token()
    if not token:
        return "Error getting Twitch token"
        
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_CHANNEL}"
    res = requests.get(url, headers=headers).json()
    
    if res.get('data') and len(res['data']) > 0:
        stream = res['data'][0]
        msg = f"🔴 СТРИМ НАЧАЛСЯ!\n\n🎮 Категория: {stream.get('game_name', 'Не указана')}\n📌 Название: {stream.get('title', 'Без темы')}\n\nhttps://twitch.tv/{TWITCH_CHANNEL}"
        
        tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": TELEGRAM_CHANNEL_ID, "text": msg})
        return "Stream is LIVE, notification sent!"
    else:
        # Тестовая отправка сообщения, если стрим оффлайн
        offline_msg = f"⚪️ Стрим {TWITCH_CHANNEL} сейчас оффлайн."
        send_telegram_message(offline_msg)
        return "Stream is OFFLINE, test notification sent!"
    
    return "Stream is offline."

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = check_and_notify()
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(result.encode('utf-8'))

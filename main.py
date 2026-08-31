import os
import time
import requests

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
    response = requests.post(url, data=data)
    return response.json().get('access_token')

def check_live():
    token = get_twitch_token()
    if not token:
        print("Ошибка получения токена Twitch")
        return False
        
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_CHANNEL}"
    res = requests.get(url, headers=headers).json()
    
    if res.get('data') and len(res['data']) > 0:
        stream = res['data'][0]
        msg = f"🔴 СТРИМ НАЧАЛСЯ!\n\n🎮 Игра: {stream.get('game_name', 'Не указана')}\n📌 Тема: {stream.get('title', 'Без темы')}\n\nhttps://twitch.tv/{TWITCH_CHANNEL}"
        
        tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": TELEGRAM_CHANNEL_ID, "text": msg})
        return True
    return False

print("Скрипт мониторинга Twitch запущен...")
is_live = False

while True:
    try:
        currently_live = check_live()
        if currently_live and not is_live:
            print("Анонс успешно отправлен в Telegram!")
            is_live = True
        elif not currently_live:
            is_live = False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        
    time.sleep(60) # Проверка каждые 60 секунд

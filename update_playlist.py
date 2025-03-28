import requests
from bs4 import BeautifulSoup

# URL канала, с которого нужно извлечь токен
channel_url = "https://onlinetv.su/tv/kino/262-sapfir.html"

# Получаем страницу канала
response = requests.get(channel_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Найдем ссылку с токеном в исходном коде страницы
video_tag = soup.find('video')
video_src = video_tag['src'] if video_tag else None

# Если ссылка найдена, обновим токен
if video_src:
    # Здесь нужно обработать ссылку, чтобы извлечь новый токен (это можно сделать через регулярные выражения или другие методы)
    new_token_url = video_src.split('?')[0]  # Убираем старый токен и оставляем базовую ссылку
    new_token_url += "?token=<новый_токен>"  # Добавьте сюда логику для получения нового токена

    # Открываем плейлист и обновляем ссылку
    with open('playlist.m3u', 'w') as file:
        file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

    print("Плейлист обновлен.")
else:
    print("Не удалось найти видео ссылку с токеном.")

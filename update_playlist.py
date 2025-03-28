import requests
from bs4 import BeautifulSoup

# URL канала, с которого нужно извлечь токен
channel_url = "https://onlinetv.su/tv/kino/262-sapfir.html"

# Заголовки для обхода кэширования (если необходимо)
headers = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

# Получаем страницу канала
response = requests.get(channel_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Найдем ссылку с токеном в исходном коде страницы
video_tag = soup.find('video')
video_src = video_tag['src'] if video_tag else None

# Если ссылка найдена, обновим токен
if video_src:
    # Выводим исходную ссылку с токеном для отладки
    print(f"Video source URL: {video_src}")

    # Здесь нужно обработать ссылку, чтобы извлечь новый токен
    new_token_url = video_src.split('?')[0]  # Убираем старый токен и оставляем базовую ссылку
    new_token_url += "?token=<новый_токен>"  # Здесь добавляется новый токен

    # Выводим новый URL для отладки
    print(f"New token URL: {new_token_url}")

    # Открываем плейлист и обновляем ссылку
    with open('playlist.m3u', 'w') as file:
        file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

    # Выводим информацию о том, что плейлист обновлен
    print(f"New playlist URL written: {new_token_url}")
else:
    # Если не удалось найти видео ссылку с токеном, выводим ошибку
    print("Не удалось найти видео ссылку с токеном.")





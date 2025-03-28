import requests
from bs4 import BeautifulSoup

# URL канала, с которого нужно извлечь токен
channel_url = "https://onlinetv.su/tv/kino/262-sapfir.html"

# Получаем страницу канала
response = requests.get(channel_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Найдем тег <video> и затем в нем <source> для получения ссылки с токеном
video_tag = soup.find('video')
if video_tag:
    source_tag = video_tag.find('source')  # Находим тег <source> внутри <video>
    if source_tag and 'src' in source_tag.attrs:
        video_src = source_tag['src']  # Получаем ссылку с токеном из атрибута src
        print("Источник видео:", video_src)

        # Обновление токена в плейлисте
        new_token_url = video_src.split('?')[0]  # Убираем старый токен и оставляем базовую ссылку
        new_token_url += "?token=<новый_токен>"  # Добавьте сюда логику для получения нового токена

        # Открываем плейлист и обновляем ссылку
        with open('playlist.m3u', 'w') as file:
            file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

        print("Плейлист обновлен.")
    else:
        print("Ошибка: тег <source> или атрибут 'src' не найден")
else:
    print("Ошибка: тег <video> не найден")


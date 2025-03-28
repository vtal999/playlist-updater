import requests
from bs4 import BeautifulSoup

# URL канала, с которого нужно извлечь токен
channel_url = "https://onlinetv.su/tv/kino/262-sapfir.html"

# Получаем страницу канала
response = requests.get(channel_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Находим ссылку на видео
video_tag = soup.find('video')
if video_tag:
    source_tag = video_tag.find('source')  # Находим тег <source> внутри <video>
    if source_tag and 'src' in source_tag.attrs:
        video_src = source_tag['src']  # Получаем ссылку с токеном из атрибута src

        # Разделяем URL и получаем базовый адрес
        base_url = video_src.split('?')[0]

        # Делаем запрос к серверу для получения нового токена
        response = requests.get(base_url)
        # Предположим, что новый токен можно найти в URL или в ответе
        # Нужно будет реализовать логику для извлечения нового токена из ответа

        # Пример: получаем новый токен из URL
        new_token = "новый_токен_из_ответа"  # Заменить на реальную логику получения

        # Формируем новый URL с новым токеном
        new_token_url = f"{base_url}?token={new_token}"

        # Записываем обновленный плейлист
        with open('playlist.m3u', 'w') as file:
            file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

        print("Плейлист обновлен.")
    else:
        print("Ошибка: тег <source> или атрибут 'src' не найден")
else:
    print("Ошибка: тег <video> не найден")




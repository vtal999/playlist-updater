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
if video_tag:
    # Находим тег <source> внутри тега <video>
    source_tag = video_tag.find('source')
    if source_tag:
        # Используем get() чтобы избежать ошибки если атрибут 'src' не существует
        video_src = source_tag.get('src')
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
            print("Не удалось найти атрибут 'src' в теге <source>")
    else:
        print("Не удалось найти тег <source> в теге <video>")
else:
    print("Не удалось найти тег <video> на странице.")







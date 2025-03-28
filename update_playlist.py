import requests
from bs4 import BeautifulSoup
import os

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
    # Используем get() чтобы избежать ошибки если атрибут 'src' не существует
    video_src = video_tag.get('src')
    if video_src:
        # Извлекаем новый токен из URL
        print(f"Video source URL: {video_src}")
        
        # Пример извлечения токена из URL
        token_start = video_src.find("token=") + len("token=")
        token_end = video_src.find("&", token_start)
        token = video_src[token_start:token_end if token_end != -1 else None]
        
        print(f"Extracted token: {token}")

        # Собираем новый URL с токеном
        new_token_url = video_src.split('?')[0] + f"?token={token}"
        
        # Обновляем содержимое файла в репозитории
        file_path = 'playlist.m3u'  # Путь к вашему плейлисту в репозитории

        # Новый контент для плейлиста
        new_playlist_content = f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n"

        # Запись нового контента в файл
        with open(file_path, 'w') as f:
            f.write(new_playlist_content)

        print(f"New playlist URL written to file: {new_token_url}")

        # Добавляем и коммитим изменения в репозиторий
        os.system(f'git add {file_path}')
        os.system(f'git commit -m "Update playlist with new token"')
        os.system(f'git push')

    else:
        print("Не удалось найти атрибут 'src' в теге <video>")
else:
    print("Не удалось найти тег <video> на странице.")










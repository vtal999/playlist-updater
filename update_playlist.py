import requests
from bs4 import BeautifulSoup
import os
import subprocess

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

# Найдем ссылку с токеном в теге <source>
source_tag = soup.find('source')
if source_tag:
    video_src = source_tag.get('src')
    if video_src:
        print(f"Video source URL: {video_src}")

        # Извлекаем токен
        start_index = video_src.find('token=') + len('token=')
        end_index = video_src.find('&', start_index)
        if end_index == -1:
            end_index = len(video_src)
        extracted_token = video_src[start_index:end_index]
        
        print(f"Extracted token: {extracted_token}")

        # Формируем новый URL
        new_token_url = video_src.split('?')[0] + f"?token={extracted_token}"
        print(f"New token URL: {new_token_url}")

        # Записываем в файл
        playlist_path = 'playlist.m3u'
        print(f"Updating playlist at: {playlist_path}")

        with open(playlist_path, 'w') as file:
            file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

        # Проверяем, что файл реально обновился
        with open(playlist_path, 'r') as file:
            print("=== CURRENT PLAYLIST CONTENT ===")
            print(file.read())
            print("================================")

        # Добавляем настройки Git перед коммитом
        subprocess.run(['git', 'config', '--global', 'user.email', 'you@example.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'Your Name'], check=True)

        # Проверяем статус Git перед коммитом
        subprocess.run(['git', 'status'], check=True)

        # Принудительно добавляем файл
        subprocess.run(['git', 'add', '-f', playlist_path], check=True)

        # Проверяем статус снова
        subprocess.run(['git', 'status'], check=True)

        # Делаем коммит и пуш
        try:
            subprocess.run(['git', 'commit', '-m', 'Update playlist with new token'], check=True)
            subprocess.run(['git', 'push'], check=True)
            print("Changes pushed to the repository.")
        except subprocess.CalledProcessError as e:
            print(f"Error during git commit/push: {e}")
    else:
        print("Не удалось найти атрибут 'src' в теге <source>")
else:
    print("Не удалось найти тег <source> на странице.")















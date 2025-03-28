import requests
from bs4 import BeautifulSoup
import os
from git import Repo

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
        
        # Обновляем плейлист
        new_playlist_content = f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n"
        
        # Убедитесь, что файл в репозитории GitHub обновляется
        repo_path = '/home/runner/work/playlist-updater/playlist-updater'  # Путь до репозитория
        playlist_path = os.path.join(repo_path, 'playlist.m3u')

        # Открываем файл для записи обновленного плейлиста
        with open(playlist_path, 'w') as file:
            file.write(new_playlist_content)
        
        # Обновляем файл в репозитории
        repo = Repo(repo_path)
        repo.git.add(playlist_path)
        repo.index.commit(f"Update playlist with new token: {token}")
        repo.remotes.origin.push()

        print(f"Playlist updated and pushed to GitHub: {new_token_url}")

    else:
        print("Не удалось найти атрибут 'src' в теге <video>")
else:
    print("Не удалось найти тег <video> на странице.")











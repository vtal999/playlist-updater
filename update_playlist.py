import requests
from bs4 import BeautifulSoup
import os
import base64

# URL канала, с которого нужно извлечь токен
channel_url = "http://ip.viks.tv/114427-22-tv.html"

# Заголовки для обхода кэширования (если необходимо)
headers = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

# Получаем страницу канала
response = requests.get(channel_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Найдем ссылку в теге <video>
video_tag = soup.find('video')
if video_tag:
    # Извлекаем ссылку из атрибута 'src' тега <video>
    video_src = video_tag.get('src')
    if video_src:
        print(f"Video URL: {video_src}")

        # Формируем новый URL
        new_url = video_src

        print(f"New URL: {new_url}")

        # Путь к плейлисту
        playlist_path = 'playlist.m3u'
        print(f"Updating playlist at: {playlist_path}")

        # Открываем плейлист и обновляем ссылку
        with open(playlist_path, 'w') as file:
            file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_url}\n")

        # Выводим содержимое файла для проверки
        with open(playlist_path, 'r') as file:
            playlist_content = file.read()
            print("Содержимое файла playlist.m3u после обновления:")
            print(playlist_content)

        # === Обновление файла через GitHub API ===
        repo_owner = "vtal999"
        repo_name = "playlist-updater"
        file_path = "playlist.m3u"
        branch = "main"
        
        # Получаем токен GITHUB_TOKEN из переменной окружения
        github_token = os.getenv("GITHUB_TOKEN")  # Используем GITHUB_TOKEN, передаваемый GitHub Actions
        print(f"GITHUB_TOKEN: {github_token}")  # Добавлено для отладки

        headers = {"Authorization": f"token {github_token}"}
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

        # Получаем информацию о текущем файле, чтобы обновить его
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            sha = file_data.get("sha", "")
        else:
            print(f"Ошибка при получении информации о файле: {response.text}")
            sha = ""

        # Кодируем содержимое плейлиста в base64
        encoded_content = base64.b64encode(playlist_content.encode()).decode()

        data = {
            "message": "Update playlist with new token",
            "content": encoded_content,
            "sha": sha,
            "branch": branch
        }

        # Отправляем запрос для обновления файла
        response = requests.put(url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            print("Файл успешно обновлен через GitHub API.")
        else:
            print("Ошибка при обновлении через API:", response.text)

    else:
        print("Не удалось найти атрибут 'src' в теге <source>")

else:
    print("Не удалось найти тег <source> на странице.")























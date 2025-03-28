import requests
from bs4 import BeautifulSoup
import os
import base64

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
    # Извлекаем ссылку из атрибута 'src' тега <source>
    video_src = source_tag.get('src')
    if video_src:
        print(f"Video source URL: {video_src}")

        # Извлекаем токен из ссылки
        start_index = video_src.find('token=') + len('token=')
        end_index = video_src.find('&', start_index)
        if end_index == -1:
            end_index = len(video_src)
        extracted_token = video_src[start_index:end_index]
        
        print(f"Extracted token: {extracted_token}")

        # Формируем новый URL с актуальным токеном
        new_token_url = video_src.split('?')[0]
        new_token_url += f"?token={extracted_token}"

        print(f"New token URL: {new_token_url}")

        # Путь к плейлисту
        playlist_path = 'playlist.m3u'
        print(f"Updating playlist at: {playlist_path}")

        # Открываем плейлист и обновляем ссылку
        with open(playlist_path, 'w') as file:
            file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

        # Выводим содержимое файла для проверки
        with open(playlist_path, 'r') as file:
            playlist_content = file.read()
            print("ФИНАЛЬНОЕ СОДЕРЖИМОЕ playlist.m3u:\n" + playlist_content)

        # === Обновление файла через GitHub API ===
        repo_owner = "vtal999"
        repo_name = "playlist-updater"
        file_path = "playlist.m3u"
        branch = "main"
        
        # Получаем персональный токен из переменной окружения
        github_token = os.getenv("MY_PERSONAL_TOKEN")  # Получаем токен из переменной окружения

        if not github_token:
            print("Ошибка: Токен не найден в переменной окружения!")
        else:
            print(f"Используется токен: {github_token[:4]}...")

        headers = {"Authorization": f"token {github_token}"}
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

        # Получаем информацию о текущем файле, чтобы обновить его
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            sha = file_data.get("sha", "")
        else:
            print(f"Ошибка при получении информации о файле: {response.status_code} - {response.text}")
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



















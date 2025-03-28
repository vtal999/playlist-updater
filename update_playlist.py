import requests
from bs4 import BeautifulSoup
import os
import base64

# URL канала с нового сайта
channel_url = "http://ip.viks.tv/114427-22-tv.html"  # Новый сайт

# Заголовки для обхода кэширования (если необходимо)
headers = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

# Получаем страницу канала
response = requests.get(channel_url, headers=headers)
if response.status_code != 200:
    print(f"Ошибка при запросе страницы: {response.status_code}")
else:
    print(f"Страница успешно загружена: {channel_url}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Здесь нужно найти ссылку с токеном в теге <video> и извлечь полный URL
    video_tag = soup.find('video')  # Ищем тег <video>
    if video_tag:
        video_src = video_tag.get('src')  # Получаем полный URL из атрибута src
        if video_src:
            print(f"Video source URL: {video_src}")

            # Формируем новый URL с актуальным токеном (если нужно подменить токен)
            new_token_url = video_src

            print(f"New token URL: {new_token_url}")

            # Путь к плейлисту
            playlist_path = 'playlist.m3u'
            print(f"Updating playlist at: {playlist_path}")

            # Открываем плейлист и обновляем ссылку
            with open(playlist_path, 'w') as file:
                file.write(f"#EXTM3U\n#EXTINF:-1, Видео\n{new_token_url}\n")

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
            if not github_token:
                print("Ошибка: GITHUB_TOKEN не найден!")
            else:
                print(f"GITHUB_TOKEN найден.")

                headers = {"Authorization": f"token {github_token}"}
                url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

                # Получаем информацию о текущем файле, чтобы обновить его
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    file_data = response.json()
                    sha = file_data.get("sha", "")
                    print(f"SHA файла: {sha}")
                else:
                    print(f"Ошибка при получении информации о файле: {response.status_code} - {response.text}")
                    sha = ""

                if sha:
                    # Кодируем содержимое плейлиста в base64
                    encoded_content = base64.b64encode(playlist_content.encode()).decode()

                    # Данные для отправки на GitHub
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
                        print(f"Ошибка при обновлении через API: {response.status_code} - {response.text}")
                else:
                    print("Не удалось получить SHA для файла.")
        else:
            print("Не удалось найти атрибут 'src' в теге <video>")
    else:
        print("Не удалось найти тег <video> на странице.")






















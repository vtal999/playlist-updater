from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64

# Настройка веб-драйвера
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Открывать браузер в фоновом режиме (без интерфейса)

# Запуск драйвера Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL канала, с которого нужно извлечь токен
channel_url = "http://ip.viks.tv/114427-22-tv.html"

# Открываем страницу
driver.get(channel_url)

# Ждем, пока тег <video> появится на странице
driver.implicitly_wait(10)

# Находим тег <video> и извлекаем атрибут 'src'
video_tag = driver.find_element(By.TAG_NAME, 'video')
if video_tag:
    video_src = video_tag.get_attribute('src')
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
    print("Не удалось найти тег <video> на странице.")

# Закрываем драйвер
driver.quit()






























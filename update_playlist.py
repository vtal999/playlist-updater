from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64
import time

# Функция для инициализации драйвера с DevTools
def init_driver():
    # Настройка опций для Chrome
    options = Options()
    options.add_argument("--headless")  # Открывать браузер в фоновом режиме (без интерфейса)

    # Включаем DevTools Protocol и логи
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}  # Включаем все логи производительности

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, desired_capabilities=caps)
    return driver

# Функция для извлечения URL видео из логов сети
def get_video_url_from_network(driver):
    # Ждем, пока страница загрузится
    time.sleep(10)  # Можно заменить на явное ожидание или метод, который будет проверять загрузку

    # Сбор всех сетевых запросов
    performance_logs = driver.get_log('performance')
    for entry in performance_logs:
        message = entry['message']
        if 'https://s.viks.tv' in message and 'm3u8' in message:
            # Извлекаем нужный URL
            start_index = message.find("https://")
            end_index = message.find("m3u8") + 4
            video_url = message[start_index:end_index]
            return video_url
    return None

# Функция для обновления плейлиста
def update_playlist(video_url):
    playlist_path = 'playlist.m3u'
    new_url = video_url
    print(f"Updating playlist at: {playlist_path}")
    
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

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise EnvironmentError("Ошибка: GITHUB_TOKEN не найден в переменных окружения.")

    headers = {"Authorization": f"token {github_token}"}
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"

    response = requests.get(url, headers=headers)
    sha = ""
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data.get("sha", "")
    elif response.status_code != 404:
        raise Exception(f"Ошибка при получении информации о файле: {response.text}")

    # Кодируем содержимое плейлиста в base64
    encoded_content = base64.b64encode(playlist_content.encode()).decode()

    data = {
        "message": "Update playlist with new token",
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print("Файл успешно обновлен через GitHub API.")
    else:
        raise Exception(f"Ошибка при обновлении через API: {response.text}")

def main():
    driver = init_driver()

    try:
        channel_url = "http://ip.viks.tv/114427-22-tv.html"
        driver.get(channel_url)

        # Получаем видео URL из сетевых запросов
        video_url = get_video_url_from_network(driver)

        if video_url:
            print(f"Video URL from network: {video_url}")
            update_playlist(video_url)
        else:
            print("Не удалось найти видео-ссылку в логах сети.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

































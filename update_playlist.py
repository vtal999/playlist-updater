from seleniumwire import webdriver  # Импортируем webdriver из seleniumwire
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

    # Создаём драйвер с использованием selenium-wire
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Возвращаем драйвер
    return driver

# Функция для перехвата сетевых запросов
def capture_network_requests(driver):
    # Слушаем все сетевые запросы
    driver.get("http://ip.viks.tv/114427-22-tv.html")  # Загружаем нужную страницу
    
    # Ждем несколько секунд, чтобы данные успели загрузиться
    time.sleep(10)
    
    # Перебираем все запросы
    for request in driver.requests:
        # Проверяем, что запрос содержит m3u8 и с правильным доменом
        if 's.viks.tv' in request.url and 'm3u8' in request.url:
            print(f"Найденный m3u8 URL: {request.url}")
            return request.url  # Возвращаем найденный URL

    return None  # Если не нашли m3u8 ссылку

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
        video_url = capture_network_requests(driver)

        if video_url:
            print(f"Найден видео URL: {video_url}")
            update_playlist(video_url)
        else:
            print("Не удалось найти видео-ссылку в логах сети.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()































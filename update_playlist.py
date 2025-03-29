from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64
import time

# Функция для инициализации драйвера с включенным DevTools для перехвата запросов
def init_driver():
    options = Options()
    options.add_argument("--headless")  # Без интерфейса (если не нужно окно браузера)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Включаем DevTools для перехвата запросов
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setCacheDisabled', {"cacheDisabled": True})

    return driver

# Функция для получения URL видео из сетевых запросов
def get_video_url(driver):
    channel_url = "http://ip.viks.tv/114427-22-tv.html"  # Замените на URL вашего сайта
    driver.get(channel_url)
    driver.implicitly_wait(10)

    video_url = None

    # Обработчик, который будет вызван для каждого запроса
    def handle_request(request):
        nonlocal video_url
        print(f"Запрос: {request['url']}")  # Логируем URL запроса
        
        # Ищем в URL запросов m3u8
        if "index.m3u8" in request['url'] and request.get('status') == 200:
            video_url = request['url']
            print(f"Найден URL видео: {video_url}")
    
    # Подключаем перехват запросов
    driver.request_interceptor = handle_request
    
    # Ожидаем некоторое время для выполнения всех запросов
    time.sleep(5)

    if video_url:
        print(f"Video URL: {video_url}")
        return video_url
    else:
        print("Не удалось найти ссылку на видео в сетевых запросах.")
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
        video_url = get_video_url(driver)
        if video_url:
            update_playlist(video_url)
        else:
            print("Не удалось обновить плейлист, так как ссылка на видео не получена.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

















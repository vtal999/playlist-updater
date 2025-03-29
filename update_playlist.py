from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64
import time

# Функция для инициализации драйвера
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Открывать браузер в фоновом режиме (без интерфейса)
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # Включаем логи performance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Функция для поиска index.m3u8 в XHR-запросах
def get_m3u8_url(driver):
    channel_url = "http://ip.viks.tv/114427-22-tv.html"
    driver.get(channel_url)
    time.sleep(5)  # Ждём загрузку
    
    logs = driver.get_log("performance")
    for log in logs:
        log_json = eval(log["message"])  # Преобразуем в словарь
        if "params" in log_json["message"] and "request" in log_json["message"]["params"]:
            request = log_json["message"]["params"]["request"]
            url = request.get("url", "")
            if "index.m3u8" in url:
                print(f"Найдена ссылка на поток: {url}")
                return url
    
    print("Не удалось найти ссылку .m3u8 в XHR-запросах.")
    return None

# Функция для обновления плейлиста
def update_playlist(video_url):
    playlist_path = 'playlist.m3u'
    print(f"Updating playlist at: {playlist_path}")
    
    with open(playlist_path, 'w') as file:
        file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{video_url}\n")

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
        video_url = get_m3u8_url(driver)
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














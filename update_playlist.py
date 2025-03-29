from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64
import json

# === Инициализация Selenium с DevTools (CDP) ===
def init_driver():
    options = Options()
    options.add_argument("--headless")  # Запуск без интерфейса
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# === Перехват видео-ссылки из Network ===
def get_video_url(driver):
    channel_url = "http://ip.viks.tv/114427-22-tv.html"
    driver.get(channel_url)
    driver.implicitly_wait(10)

    # Перехватываем сетевые запросы
    logs = driver.execute_script("return window.performance.getEntries();")

    for log in logs:
        url = log["name"]
        if ".m3u8" in url:  # Проверяем, есть ли в URL .m3u8
            print(f"✅ Найдена видео-ссылка: {url}")

            # Получаем куки для работы ссылки
            cookies = driver.get_cookies()
            cookie_jar = {cookie['name']: cookie['value'] for cookie in cookies}

            return url, cookie_jar

    print("❌ Не удалось найти ссылку на видео в сетевых запросах.")
    return None, None

# === Обновление плейлиста ===
def update_playlist(video_url):
    playlist_path = 'playlist.m3u'
    
    with open(playlist_path, 'w') as file:
        file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{video_url}\n")

    print("✅ Плейлист обновлен!")

    # Читаем обновленный плейлист
    with open(playlist_path, 'r') as file:
        playlist_content = file.read()

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

    encoded_content = base64.b64encode(playlist_content.encode()).decode()

    data = {
        "message": "Update playlist with new token",
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print("✅ Файл успешно обновлен через GitHub API.")
    else:
        raise Exception(f"❌ Ошибка при обновлении через API: {response.text}")

# === Основная функция ===
def main():
    driver = init_driver()

    try:
        video_url, cookies = get_video_url(driver)
        if video_url:
            update_playlist(video_url)
        else:
            print("⚠️ Ссылка не найдена, обновление плейлиста невозможно.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()


















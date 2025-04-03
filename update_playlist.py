from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64
from concurrent.futures import ThreadPoolExecutor
import time

# Функция для инициализации драйвера
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Обновленный headless-режим
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.set_page_load_timeout(120)  # Увеличиваем таймаут до 120 секунд
    return driver

# Функция для получения видео URL
def get_video_url(channel_name, channel_url):
    driver = init_driver()
    try:
        print(f"Открываю: {channel_url}")
        driver.get(channel_url)

        # Даем время странице прогрузиться
        time.sleep(10)  # 10 секунд пауза перед дальнейшими действиями

        # Проверяем, загрузилась ли страница
        if driver.execute_script("return document.readyState") != "complete":
            print(f"Страница {channel_url} загружается слишком долго...")
            return None

        # Ждем появления <video>
        wait = WebDriverWait(driver, 30)  # Увеличиваем время ожидания до 30 секунд
        try:
            video_tag = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        except Exception:
            print(f"Видео тег не найден на {channel_url}")
            print(driver.page_source[:500])  # Логируем первые 500 символов HTML
            return None

        # Поиск источника видео
        source_tag = video_tag.find_elements(By.TAG_NAME, 'source')
        video_src = source_tag[0].get_attribute('src') if source_tag else video_tag.get_attribute('src')

        if video_src:
            video_src = video_src.split("&remote=")[0]  # Убираем IP
            print(f"Найден поток для {channel_name}: {video_src}")
            return channel_name, video_src
        else:
            print(f"Не удалось найти поток для {channel_name}.")
            return None
    except Exception as e:
        print(f"Ошибка при обработке {channel_name}: {e}")
        return None
    finally:
        driver.quit()

# Функция для обновления плейлиста
def update_playlist(video_urls):
    playlist_path = 'playlist.m3u'
    print(f"Обновляю плейлист: {playlist_path}")

    with open(playlist_path, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for channel_name, video_url in video_urls.items():
            file.write(f"#EXTINF:-1, {channel_name}\n{video_url}\n")

    # GitHub API для обновления файла
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
    sha = response.json().get("sha", "") if response.status_code == 200 else ""

    encoded_content = base64.b64encode(open(playlist_path, 'rb').read()).decode('utf-8')

    data = {"message": "Автообновление плейлиста", "content": encoded_content, "sha": sha, "branch": branch}
    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print("Файл успешно обновлен в GitHub.")
    else:
        raise Exception(f"Ошибка обновления через API: {response.text}")

# Основная функция
def main():
    channels = {
        "Сапфир": "https://onlinetv.su/tv/kino/262-sapfir.html",
        "2+2": "http://ip.viks.tv/114427-22-tv.html",
        "СТБ": "http://ip.viks.tv/032117-stb.html",
        "Первый канал": "http://ip.viks.tv/021612-pervyy-kanal.html",
        "Россия 1": "http://ip.viks.tv/031327-rossiya1_tv.html",
        "Россия 24": "http://ip.viks.tv/126307-rossiya_24_tv.html",
        "НСТ": "http://ip.viks.tv/394-nst_4.html",
        "Кинохит": "http://ip.viks.tv/477-kinohit_14.html",
    }

    video_urls = {}

    # Запускаем в несколько потоков
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        results = executor.map(lambda item: get_video_url(*item), channels.items())

    for result in results:
        if result:
            channel_name, video_url = result
            video_urls[channel_name] = video_url

    if video_urls:
        update_playlist(video_urls)

if __name__ == "__main__":
    main()
























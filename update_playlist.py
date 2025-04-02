from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64

# Функция для инициализации драйвера
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Открывать браузер в фоновом режиме (без интерфейса)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Функция для обновления плейлиста
def update_playlist(video_urls):
    playlist_path = 'playlist.m3u'
    print(f"Updating playlist at: {playlist_path}")

    # Обновляем плейлист для каждого канала
    with open(playlist_path, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for channel_name, video_url in video_urls.items():
            file.write(f"#EXTINF:-1, {channel_name}\n{video_url}\n")

    # Выводим содержимое файла для проверки
    with open(playlist_path, 'r', encoding='utf-8') as file:
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
    encoded_content = base64.b64encode(playlist_content.encode('utf-8')).decode('utf-8')

    data = {
        "message": "Update playlist with new tokens",
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print("Файл успешно обновлен через GitHub API.")
    else:
        raise Exception(f"Ошибка при обновлении через API: {response.text}")

# Функция для получения видео URL с проверки на <source>
def get_video_url(driver, channel_url):
    driver.get(channel_url)
    driver.implicitly_wait(10)

    # Находим тег <video> и проверяем наличие внутри него <source>
    video_tag = driver.find_element(By.TAG_NAME, 'video')
    if video_tag:
        # Проверяем наличие тега <source> внутри тега <video>
        source_tag = video_tag.find_elements(By.TAG_NAME, 'source')
        if source_tag:
            # Если <source> найден, берем src из него
            video_src = source_tag[0].get_attribute('src') if source_tag else None
        else:
            # Если <source> нет, берем src из самого тега <video>
            video_src = video_tag.get_attribute('src')
        
        if video_src:
            print(f"Video URL для {channel_url}: {video_src}")
            return video_src
    else:
        print(f"Не удалось найти тег <video> на странице {channel_url}.")
    return None

def main():
    driver = init_driver()

    try:
        # Список каналов и их URL
        channels = {
            "Сапфир": "http://ip.viks.tv/114427-22-tv.html",
            "НТВ": "http://ip.viks.tv/032117-stb.html",
            "Первый канал": "http://ip.viks.tv/021612-pervyy-kanal.html",
            "Россия 1": "http://ip.viks.tv/031327-rossiya1_tv.html",
            "Россия 24": "http://ip.viks.tv/126307-rossiya_24_tv.html",
            # Добавьте другие каналы по аналогии
        }

        video_urls = {}

        for channel_name, channel_url in channels.items():
            video_url = get_video_url(driver, channel_url)
            if video_url:
                video_urls[channel_name] = video_url

        if video_urls:
            update_playlist(video_urls)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()


















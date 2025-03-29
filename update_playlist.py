from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64

# Функция для инициализации драйвера с заголовками
def init_driver():
    options = Options()
    options.add_argument("--headless")  # Открывать браузер в фоновом режиме (без интерфейса)
    options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0")
    options.add_argument("Referer=http://ip.viks.tv/")
    options.add_argument("Origin=http://ip.viks.tv/")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Получаем cookies и другие заголовки из браузера
def get_cookies_and_headers(driver):
    cookies = driver.get_cookies()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0',
        'Referer': 'http://ip.viks.tv/',
        'Origin': 'http://ip.viks.tv/'
    }
    return cookies, headers

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

# Основной процесс
def main():
    driver = init_driver()
    try:
        # Открываем страницу
        channel_url = "http://ip.viks.tv/114427-22-tv.html"
        driver.get(channel_url)
        
        # Ожидаем загрузки элемента <video> перед тем, как продолжить
        video_tag = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )

        # Получаем cookies и заголовки
        cookies, headers = get_cookies_and_headers(driver)

        # Извлекаем ссылку
        video_src = video_tag.get_attribute('src') if video_tag else None

        if video_src:
            print(f"Video URL: {video_src}")

            # Создаем сессию с cookies
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # Выполняем запрос с сессией и заголовками
            response = session.get(video_src, headers=headers)
            if response.status_code == 200:
                print("Видео доступно.")
                update_playlist(video_src)
            else:
                print(f"Ошибка при запросе видео: {response.status_code}")
        else:
            print("Не удалось найти тег <video> на странице.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()













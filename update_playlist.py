from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import base64

# Функция для инициализации драйвера с cookies
def init_driver_with_cookies():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск без интерфейса
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Открываем страницу, чтобы установить cookies
    driver.get("http://ip.viks.tv/114427-22-tv.html")

    # Пример добавления cookies
    cookies = [
        {'name': 'IDE', 'value': 'AHWqTUkYcnP5qWuWeCec2kArikuNMa6qaPwJ2c68Kagkr3n2H18L2tuGY4PWYosE', 'domain': '.doubleclick.net', 'path': '/'},
        {'name': 'UUID', 'value': 'ec209aeb-1283-55ad-8a81-96a2cf31b0b6', 'domain': '.srvd2204.com', 'path': '/'},
        {'name': '_ga', 'value': 'GA1.1.1605079928.1743259499', 'domain': '.viks.tv', 'path': '/'},
        {'name': 'csc', 'value': '913-1743345893366-781-1--', 'domain': '.srvd2204.com', 'path': '/'},
        {'name': 'ec_v50fr', 'value': '56cdbf5fbe1545fee8326434e5daf21f', 'domain': 'ip.viks.tv', 'path': '/'}
    ]

    for cookie in cookies:
        driver.add_cookie(cookie)  # Добавляем каждый cookie

    driver.refresh()  # Обновляем страницу с установленными cookies

    return driver

# Функция для получения ссылки на видео
def get_video_url(driver):
    video_tag = driver.find_element(By.TAG_NAME, 'video')
    video_url = video_tag.get_attribute('src') if video_tag else None
    return video_url

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
    driver = init_driver_with_cookies()

    try:
        # Получаем ссылку на видео
        video_url = get_video_url(driver)
        
        if video_url:
            print(f"Video URL: {video_url}")
            update_playlist(video_url)
        else:
            print("Не удалось найти тег <video> на странице.")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

















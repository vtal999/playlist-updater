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
        "Россия 1": "https://onlinetv.su/tv/public/302-rossija-1.html",
        "НТВ": "https://onlinetv.su/tv/public/6-ntv.html",
        "Рен ТВ": "https://onlinetv.su/tv/public/316-ren-tv.html",
        "Первый канал": "https://onlinetv.su/tv/public/246-pervyj-kanal.html",
		"Домашний": "https://onlinetv.su/tv/public/318-domashnij.html",
        "Звезда": "https://onlinetv.su/tv/public/310-zvezda.html",
        "ТВ Центр": "https://onlinetv.su/tv/public/9-tv-centr.html",
        "Пятый канал": "https://onlinetv.su/tv/public/330-pjatyj-kanal.html",
        "РТР-Планета": "https://onlinetv.su/tv/public/218-rtr-planeta.html",
        "Мир": "https://onlinetv.su/tv/public/18-mir.html",
        "Россия-Культура": "https://onlinetv.su/tv/educational/216-rossija-kultura.html",		
        "Красная линия": "https://onlinetv.su/tv/public/233-krasnaja-linija.html",
        "ОТР": "https://onlinetv.su/tv/public/11-otr.html",
        "Первый Крымский": "https://onlinetv.su/tv/public/14-pervyj-krymskij.html",
        "Спас": "https://onlinetv.su/tv/public/20-spas.html",
		"Домашний": "https://onlinetv.su/tv/public/15-8-kanal.html",
        "8 канал": "https://onlinetv.su/tv/public/310-zvezda.html",        
        "Amedia Premium": "https://onlinetv.su/tv/kino/404-amedia-premium.html",
        "Амедиа 2": "https://onlinetv.su/tv/kino/403-amedia-2.html",
        "Амедиа 1": "https://onlinetv.su/tv/kino/402-amedia-1.html",
        "КиноСезон": "https://onlinetv.su/tv/kino/353-kinosezon.html",
        "Классика Кино": "https://onlinetv.su/tv/kino/352-klassika-kino.html",
        "Советское кино": "https://onlinetv.su/tv/kino/351-sovetskoe-kino.html",
        "Любимое кино": "https://onlinetv.su/tv/kino/350-ljubimoe-kino.html",
        "Дом кино": "https://onlinetv.su/tv/kino/317-dom-kino.html",
        "Кино ТВ": "https://onlinetv.su/tv/kino/315-kino-tv.html",
        "НТВ Хит": "https://onlinetv.su/tv/kino/314-ntv-hit.html",
        "Дорама": "https://onlinetv.su/tv/kino/309-dorama.html",
        "Русский бестселлер": "https://onlinetv.su/tv/kino/308-russkij-bestseller.html",
        "Русский детектив": "https://onlinetv.su/tv/kino/304-russkij-detektiv.html",
        "Русский роман": "https://onlinetv.su/tv/kino/301-russkij-roman.html",
        "Киноджем 2": "https://onlinetv.su/tv/kino/291-kinojam-2.html",
        "Киноджем 1": "https://onlinetv.su/tv/kino/290-kinojam-1.html",
        "Победа": "https://onlinetv.su/tv/kino/257-pobeda.html",
        "Кинопоказ": "https://onlinetv.su/tv/kino/222-kinopokaz.html",
        "Мосфильм золотая коллекция": "https://onlinetv.su/tv/kino/126-mosfilm-zolotaja-kollekcija.html",
        "Ретро тв": "https://onlinetv.su/tv/kino/125-retro-tv.html",
        "Red": "https://onlinetv.su/tv/kino/118-red.html",
        "Black": "https://onlinetv.su/tv/kino/117-black.html",
        "Bollywood HD": "https://onlinetv.su/tv/kino/116-bollywood.html",
        "Еврокино": "https://onlinetv.su/tv/kino/115-evrokino.html",
        "Мир сериала": "https://onlinetv.su/tv/kino/113-mir-seriala.html",
        "Hollywood": "https://onlinetv.su/tv/kino/107-hollywood.html",
        "Русский иллюзион": "https://onlinetv.su/tv/kino/106-russkij-illjuzion.html",
        "Фокс": "https://onlinetv.su/tv/kino/103-fox.html",
        "Фокс лайф": "https://onlinetv.su/tv/kino/102-fox-life.html",
        "КиноСат": "https://onlinetv.su/tv/kino/100-kinosat.html",
        "Фантастика": "https://onlinetv.su/tv/kino/99-fantastika-hd.html",
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
























import requests
import re
import os
import base64
from concurrent.futures import ThreadPoolExecutor
import logging

# Настройка логирования
logging.basicConfig(filename='playlist_update.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_video_url(channel_name, channel_url, existing_urls):
    try:
        print(f"Открываю: {channel_url}")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
        response = requests.get(channel_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Ищем ссылку на поток
        match = re.search(r'(https?://[^"]+\.m3u8[^"]*)', response.text)
        if match:
            video_src = match.group(1)
            # Убираем часть после &remote=
            video_src = video_src.split("&remote=")[0]
            
            if existing_urls.get(channel_name) != video_src:
                print(f"Найден поток для {channel_name}: {video_src}")
                return channel_name, video_src
            else:
                print(f"Для {channel_name} ссылка не изменилась.")
                return None
        else:
            logging.error(f"Не удалось найти поток для {channel_name}.")
            return None
    except requests.exceptions.Timeout:
        logging.error(f"Таймаут при подключении к {channel_name}.")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при обработке {channel_name}: {e}")
        return None

def update_playlist(video_urls, existing_urls):
    playlist_path = 'playlist.m3u'
    print(f"Обновляю плейлист: {playlist_path}")
    
    updated = False
    with open(playlist_path, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for channel_name, video_url in existing_urls.items():
            file.write(f"#EXTINF:-1, {channel_name}\n{video_url}\n")
        
        # Обновляем только изменившиеся ссылки
        for channel_name, video_url in video_urls.items():
            if video_url:
                file.write(f"#EXTINF:-1, {channel_name}\n{video_url}\n")
                updated = True
    
    if updated:
        print("Плейлист обновлен.")
    else:
        print("Нет изменений в плейлисте.")

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

def main():
    channels = {
        "Сапфир": "https://onlinetv.su/tv/kino/262-sapfir.html",
        "Amedia Premium": "https://onlinetv.su/tv/kino/404-amedia-premium.html",
        "Амедиа 2": "https://onlinetv.su/tv/kino/403-amedia-2.html",
        "Амедиа 1": "https://onlinetv.su/tv/kino/402-amedia-1.html",
        "КиноСезон": "https://onlinetv.su/tv/kino/353-kinosezon.html",
        "Классика Кино": "https://onlinetv.su/tv/kino/352-klassika-kino.html",
        "Советское кино": "https://onlinetv.su/tv/kino/351-sovetskoe-kino.html",
        "Любимое кино": "https://onlinetv.su/tv/kino/350-ljubimoe-kino.html",
        "Дом кино": "https://onlinetv.su/tv/kino/317-dom-kino.html",
        "НТВ Хит": "https://onlinetv.su/tv/kino/314-ntv-hit.html",
        "Дорама": "https://onlinetv.su/tv/kino/309-dorama.html",
        "Русский бестселлер": "https://onlinetv.su/tv/kino/308-russkij-bestseller.html",
        "Русский детектив": "https://onlinetv.su/tv/kino/304-russkij-detektiv.html",
        "Русский роман": "https://onlinetv.su/tv/kino/301-russkij-roman.html",
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
		"НТВ Сериал": "https://onlinetv.su/tv/kino/98-ntv-serial.html",
        "Шокирующее HD": "https://onlinetv.su/tv/kino/86-shokirujuschee-hd.html",
        "Страшное HD": "https://onlinetv.su/tv/kino/85-strashnoe-hd.html",
        "О Кино": "https://onlinetv.su/tv/kino/79-o-kino.html",
        "Paramount Comedy": "https://onlinetv.su/tv/entertainment/37-comedy-central.html",
        "Телекафе": "https://onlinetv.su/tv/entertainment/34-telekafe.html",
        "тв3": "https://onlinetv.su/tv/kino/7-tv-3.html",
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
        "8 канал": "https://onlinetv.su/tv/public/15-8-kanal.html",
        "Соловьев Лайф": "https://onlinetv.su/tv/news/313-solovev-live.html",
        "Евроньюс": "https://onlinetv.su/tv/news/305-euronews.html",
        "Россия 24": "https://onlinetv.su/tv/news/217-rossija-24.html",
        "RTVi": "https://onlinetv.su/tv/news/186-rtvi.html",		
        "CGTN русский": "https://onlinetv.su/tv/news/184-cgtn.html",
        "Deutsche Welle": "https://onlinetv.su/tv/news/183-dw-news.html",
        "Беларусь 24": "https://onlinetv.su/tv/news/132-belarus-24.html",
        "Дождь": "https://onlinetv.su/tv/news/124-dozhd.html",
		"Известия": "https://onlinetv.su/tv/news/28-izvestija.html",
        "Вести ФМ": "https://onlinetv.su/tv/news/22-vesti-fm.html",			
        "Пятница": "https://onlinetv.su/tv/entertainment/41-pjatnica.html",
        "Анекдот ТВ": "https://onlinetv.su/tv/entertainment/341-anekdot-tv.html",
        "Ювелирочка": "https://onlinetv.su/tv/entertainment/332-juvelirochka.html",
        "ТНТ": "https://onlinetv.su/tv/entertainment/329-tnt.html",		
        "СТС Лав": "https://onlinetv.su/tv/entertainment/307-sts-love.html",
        "Сарафан": "https://onlinetv.su/tv/entertainment/225-sarafan.html",
        "СТС": "https://onlinetv.su/tv/entertainment/224-sts.html",
        "Москва Доверие": "https://onlinetv.su/tv/entertainment/189-moskva-doverie.html",
		"Мужской": "https://onlinetv.su/tv/sport/136-muzhskoj.html",
        "2х2": "https://onlinetv.su/tv/entertainment/61-2x2.html",			
        "Канал Ю": "https://onlinetv.su/tv/entertainment/44-kanal-ju.html",
        "Че": "https://onlinetv.su/tv/entertainment/43-che.html",
        "Суббота": "https://onlinetv.su/tv/entertainment/40-subbota.html",
		"ТНТ 4": "https://onlinetv.su/tv/entertainment/39-tnt4.html",
        "World Fashion Channel": "https://onlinetv.su/tv/entertainment/38-world-fashion.html",		
        "Канал Еда": "https://onlinetv.su/tv/entertainment/33-eda.html",
    }
    
    # Считываем существующие ссылки из плейлиста
    existing_urls = {}
    if os.path.exists('playlist.m3u'):
        with open('playlist.m3u', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(1, len(lines), 2):
                if i-1 < len(lines):
                    channel_name_line = lines[i-1].strip()
                    video_url_line = lines[i].strip()
                    if channel_name_line.startswith("#EXTINF:") and video_url_line:
                        channel_name = channel_name_line.split(",")[1].strip()
                        existing_urls[channel_name] = video_url_line

    video_urls = {}
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(lambda item: get_video_url(*item, existing_urls), channels.items())
    
    for result in results:
        if result:
            channel_name, video_url = result
            video_urls[channel_name] = video_url
    
    if video_urls:
        update_playlist(video_urls, existing_urls)

if __name__ == "__main__":
    main()



























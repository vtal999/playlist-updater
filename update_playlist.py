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
        "Страшное HD": "https://onlinetv.su/tv/kino/85-strashnoe-hd.html",
        "СТС": "https://onlinetv.su/tv/entertainment/224-sts.html",
    }
    
    # Считываем существующие ссылки из плейлиста
    existing_urls = {}
    if os.path.exists('playlist.m3u'):
        with open('playlist.m3u', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(1, len(lines), 2):
                channel_name = lines[i-1].strip().split(",")[1].strip()
                video_url = lines[i].strip()
                existing_urls[channel_name] = video_url

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


























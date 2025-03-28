import requests
from bs4 import BeautifulSoup

# URL канала, с которого нужно извлечь токен
channel_url = "https://onlinetv.su/tv/kino/262-sapfir.html"

# Заголовки для обхода кэширования (если необходимо)
headers = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

# Получаем страницу канала
response = requests.get(channel_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Найдем тег <video> и извлечем ссылку из тега <source>
video_tag = soup.find('video')
if video_tag:
    # Ищем тег <source> внутри <video>, где будет ссылка с токеном
    source_tag = video_tag.find('source')
    if source_tag:
        # Получаем ссылку из атрибута src тега <source>
        video_src = source_tag.get('src')
        if video_src:
            # Выводим исходную ссылку с токеном для отладки
            print(f"Video source URL: {video_src}")

            # Извлекаем токен из URL
            token_start = video_src.find("token=") + len("token=")
            token_end = video_src.find("&", token_start)
            if token_end == -1:
                token_end = len(video_src)
            
            token = video_src[token_start:token_end]

            # Выводим извлеченный токен
            print(f"Extracted token: {token}")

            # Обновляем URL, убирая старый токен, и записываем новый токен
            new_token_url = video_src.split('?')[0]  # Получаем базовую ссылку
            new_token_url += f"?token={token}"  # Добавляем новый токен

            # Выводим новый URL для отладки
            print(f"New token URL: {new_token_url}")

            # Открываем плейлист и обновляем ссылку
            with open('playlist.m3u', 'w') as file:
                file.write(f"#EXTM3U\n#EXTINF:-1, Сапфир\n{new_token_url}\n")

            # Выводим информацию о том, что плейлист обновлен
            print(f"New playlist URL written: {new_token_url}")
        else:
            print("Не удалось найти ссылку с токеном в теге <source>")
    else:
        print("Не удалось найти тег <source> внутри <video>")
else:
    print("Не удалось найти тег <video> на странице.")









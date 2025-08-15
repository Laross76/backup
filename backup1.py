from dotenv import load_dotenv
import os
import requests
from datetime import datetime


# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токены из переменных окружения
vk_token = os.getenv('VK_TOKEN')
ya_token = os.getenv('YA_TOKEN')

# Проверяем, что токены заданы
if not vk_token or not ya_token:
    print("Токены не заданы в .env файле")
    exit()

# Выводы для проверки токенов
print(f"VK_TOKEN: {vk_token}")
print(f"YA_TOKEN: {ya_token}")

def get_vk_photos(user_id, token):
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'album_id': 'profile',
        'rev': 1,
        'access_token': token,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Проверка на ошибки
    return response.json()['response']['items']

def main():
    user_id = input('809625875').strip()
    photos = get_vk_photos(user_id, vk_token)

    if not photos:
        print("Нет фотографий для отображения.")
        return

    print("Полученные фотографии:")
    for photo in photos:
        print(photo)

    # Сортируем фотографии по количеству лайков и дате
    top_photos = sorted(photos, key=lambda x: (x['likes']['count'], x['date']), reverse=True)[:5]

    print("Топ-5 фотографий по количеству лайков:")
    for photo in top_photos:
        likes = photo['likes']['count']
        date = datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Фото ID: {photo['id']}, Лайки: {likes}, Дата: {date}")

if __name__ == '__main__':
    main()












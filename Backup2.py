from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import json
from tqdm import tqdm  # Для прогресс-бара

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

def create_yandex_folder(folder_name, token):
    url = f'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Authorization': f'OAuth {token}'
    }
    params = {
        'path': folder_name,
        'overwrite': 'true'
    }
    response = requests.put(url, headers=headers, params=params)
    response.raise_for_status()  # Проверка на ошибки

def upload_photo_to_yandex(photo_url, file_name, token):
    url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {
        'Authorization': f'OAuth {token}'
    }
    params = {
        'path': file_name,
        'url': photo_url
    }
    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status()  # Проверка на ошибки

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
    photo_info_list = []
    for photo in top_photos:
        likes = photo['likes']['count']
        date = datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d %H-%M-%S')
        file_name = f"{likes}_{date}.jpg"

        # Проверка на дубликаты
        existing_files = [info['file_name'] for info in photo_info_list]
        while file_name in existing_files:
            likes += 1  # Увеличиваем лайки для уникальности
            file_name = f"{likes}_{date}.jpg"

        photo_info_list.append({
            'file_name': file_name,
            'likes': likes,
            'date': date,
            'url': photo['sizes'][-1]['url']  # Берем самую большую версию фото
        })

    # Создаем папку на Яндекс.Диске
    folder_name = 'VK_Photos'
    create_yandex_folder(folder_name, ya_token)

    # Загружаем фотографии на Яндекс.Диск
    print("Загрузка фотографий на Яндекс.Диск...")
    for photo_info in tqdm(photo_info_list, desc="Загрузка"):
        upload_photo_to_yandex(photo_info['url'], f"{folder_name}/{photo_info['file_name']}", ya_token)

    # Сохраняем информацию о файлах в JSON
    with open('uploaded_photos.json', 'w') as json_file:
        json.dump(photo_info_list, json_file, indent=4)

print("Загрузка завершена. Информация о загруженных фотографиях сохранена в uploaded_photos.json.")

if __name__ == '__main__':
    main()

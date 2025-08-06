import json
import requests
from tqdm import tqdm

VK_API_VERSION = '5.131'


def get_vk_photos(user_id, vk_token):
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1,
        'count': 1000,
        'access_token': vk_token,
        'v': VK_API_VERSION,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    if 'error' in data:
        raise Exception(data['error']['error_msg'])
    return data['response']['items']


def largest_photos(photos, count=5):
    def max_area(photo):
        sizes = photo['sizes']
        max_s = max(sizes, key=lambda s: s['width'] * s['height'])
        return max_s['width'] * max_s['height']
    photos_sorted = sorted(photos, key=max_area, reverse=True)
    return photos_sorted[:count]


def get_max_size_photo(photo):
    sizes = photo['sizes']
    return max(sizes, key=lambda s: s['width'] * s['height'])


def create_ya_folder(token, folder):
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Authorization': f'OAuth {token}'}
    params = {'path': folder}
    r = requests.put(url, headers=headers, params=params)
    if r.status_code not in (201, 409):
        r.raise_for_status()


def get_upload_url(token, disk_path):
    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Authorization': f'OAuth {token}'}
    params = {'path': disk_path, 'overwrite': 'true'}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json()['href']


def upload_file(token, disk_path, file_url):
    upload_url = get_upload_url(token, disk_path)
    r = requests.get(file_url, stream=True)
    r.raise_for_status()
    with requests.put(upload_url, data=r.iter_content(1024*1024)) as upload_resp:
        if upload_resp.status_code not in (201, 202):
            upload_resp.raise_for_status()


def main():
    user_id = input('ID пользователя ВК').strip()
    vk_token = input('VK access_token').strip()
    ya_token = input('токен Яндекс.Диска').strip()

    photos = get_vk_photos(user_id, vk_token)
    top_photos = largest_photos(photos, 5)

    folder = f'vk_photos_{user_id}'
    create_ya_folder(ya_token, folder)

    used_names = set()
    result = []

    for photo in tqdm(top_photos, desc='Загрузка фото'):
        max_photo = get_max_size_photo(photo)
        likes = photo['likes']['count']
        name = f'{likes}.jpg'
        if name in used_names:
            suffix = 1
            while f'{likes}_{suffix}.jpg' in used_names:
                suffix += 1
            name = f'{likes}_{suffix}.jpg'
        used_names.add(name)

        disk_path = f'{folder}/{name}'
        upload_file(ya_token, disk_path, max_photo['url'])

        
        result.append({'file_name': name, 'size': 'z'}) 

    
    with open('photos_info.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f'Загрузка завершена. Фотографии в папке "{folder}" на Яндекс.Диске.')
    print('Информация сохранена в photos_info.json')


if __name__ == '__main__':
    main()
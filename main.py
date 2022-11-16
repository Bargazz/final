import requests
import json
from tqdm import tqdm
from vk_token import vk_token, user_id
from token_yandex import ya_token


def max_res(photo_sizes):
    max_res = 0
    desired_obj = 0
    for index in range(len(photo_sizes)):
        get_size = photo_sizes[index]['height'] * photo_sizes[index]['width']
        if get_size > max_res:
            max_res = get_size
            desired_obj = index
    return photo_sizes[desired_obj].get('url'), photo_sizes[desired_obj].get('type')


class VkInfo:
    def __init__(self, token, count='5', ver='5.131', album_id='profile'):
        self.token = token
        self.id = user_id
        self.count = count
        self.version = ver
        self.alb = album_id

    def photo_info(self):
        params = {
            'album_id': self.alb,
            'access_token': self.token,
            'extended': '1',
            'v': self.version,
            'count': self.count
        }
        uri = 'https://api.vk.com/method/'
        url = uri + 'photos.get'
        get_json = requests.get(url, params=params).json()
        response = get_json['response']
        return response

    def get_dict_info(self):
        photo_items = self.photo_info()['items']
        list_info = []
        for item in photo_items:
            num_of_likes = item['likes']['count']
            max_size = max_res(item['sizes'])
            list_info.append({'name': f'{num_of_likes}.png', 'sizes': max_size[1], 'url': max_size[0]})
        return list_info


class YaDisk:
    def __init__(self, token, folder_name, photos_count='5'):
        self.token = token
        self.path = folder_name
        self.count = photos_count
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "Content_Type": "application/json"
        }

    def folder_create(self):
        params = {'path': self.path}
        create_folder = requests.put(self.url, headers=self.headers, params=params)
        if create_folder.status_code == 409:
            return 'Такая папка уже существует, файлы будут загружены в неё'
        return 'Папка создана'

    def upload_to_folder(self, photo_info):
        self.folder_create()
        upload_url = self.url+'/upload'
        for index in tqdm(range(len(photo_info)), desc="Прогресс загрузки файлов", unit=" File"):
            photo_ext = photo_info[index]['name']
            url_photo = photo_info[index]['url']
            param = {'path': f'{self.path}/{photo_ext}', 'url': url_photo}
            requests.post(upload_url, headers=self.headers, params=param)
        return 'Файлы загружены'


call_vk = VkInfo(vk_token)
with open('some_file.json', 'w') as file:
    json.dump(call_vk.get_dict_info(), file, indent=4)

call_yandex = YaDisk(ya_token, 'папка123')

print(call_yandex.upload_to_folder(call_vk.get_dict_info()))

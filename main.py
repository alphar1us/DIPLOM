import requests
# import pprint
import PySimpleGUI
import time


def vk_download():
    id_vk = int(input("Введите id пользователя: "))
    pictures = {}
    uri_vk = "https://api.vk.com/method/photos.get?owner_id="
    version = "&v=5.131"
    tok_test =input("Введите токен VK: ")
    access_token = "&album_id=wall&extended=1&access_token" \
                   "=" + tok_test
    url = uri_vk + str(id_vk) + access_token + version
    response = requests.get(url=url)
    if response.status_code != 200:
        print("Неверный ответ с сервера\n")
    else:
        for object_ in response.json()['response']['items']:
            max_size = 0
            url_picture = []
            pictures[object_['id']] = []
            pictures[object_['id']].append(object_['likes']['count'])
            pictures[object_['id']].append(object_['date'])
            for size in object_['sizes']:
                if size['height'] > max_size:
                    max_size = size['height']
                    url_picture = size['url']
            pictures[object_['id']].append(url_picture)
        print("Данные получены. Можно начинать загрузку\n")
        return pictures


def ya_disk_upload(data, index):
    token = input("Введите свой токен от яндекс.Диска: ")
    ya_headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token}'}
    ya_upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload?"

    for i, ids in enumerate(data):
        PySimpleGUI.one_line_progress_meter('Загрузка в Яндекс Диск', i + 1, len(data), 'Файлы: ')
        time.sleep(1)
        correct_url = "&url="
        # ya_params = f"path=%2Fnetology%2F{ids}.jpg"
        ya_params = f"path={ids}.jpg"
        for symbol in data[ids][index]:
            if symbol == "/":
                correct_url += "%2F"
            elif symbol == "=":
                correct_url += "%3D"
            elif symbol == ":":
                correct_url += "%3A"
            elif symbol == "?":
                correct_url += "%3F"
            elif symbol == "&":
                correct_url += "%26"
            else:
                correct_url += symbol
        url = ya_upload_url + ya_params + correct_url
        requests.post(url=url, headers=ya_headers)
        with open("upload.txt", "a", encoding="utf-8") as file:
            file.write(f"{ids}.jpg\n")
    print("Данные загружены\n")


answer = 0
pictures = []
element_id = 0
while answer != 4:
    print("1 - скачать с VK\n2 - загрузить на яндекс диск\n3 - выход")
    answer = int(input())
    if answer == 1:
        pictures = vk_download()
        element_id = 2
    elif answer == 2:
        if pictures:
            ya_disk_upload(pictures, element_id)
        else:
            print("Не указали откуда скачивать фото\n")
    else:
        break
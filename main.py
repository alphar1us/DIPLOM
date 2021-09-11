import requests
from pprint import pprint
from datetime import datetime
import json


class YaUploader:

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_status(self, url):
        return requests.get(url, headers={"Authorization": "OAuth " + self.access_token}).json()['status']

    def upload(self, file_name, file_url):
        requests.put("https://cloud-api.yandex.net/v1/disk/resources?path=%2Fvk_backup",
                     headers={"Authorization": "OAuth " + self.access_token})
        download_url = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload?url='
                                     + file_url.replace('/', '%2F').replace(":", "%3A")
                                     + "&path=%2Fvk_backup%2F" + file_name,
                                     headers={"Authorization": "OAuth " + self.access_token})
        if download_url.status_code == 202:
            print('Start download process')
            while self.get_status(download_url.json()['href']) == 'in-progress':
                if self.get_status(download_url.json()['href']) == 'failed':
                    print("Download failed")
                continue
            if self.get_status(download_url.json()['href']) == 'success':
                print("Successfully downloaded")
        else:
            print("Error")
            pprint(download_url.json())


class VkBackup:

    access_token = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"

    def __init__(self, vk_id: str):
        self.vk_id = vk_id

    @staticmethod
    def set_photo_name(output_date, photo):
        for date in output_date:
            if str(photo['likes']['count']) + ".jpg" == date['file_name']:
                photo_date = datetime.fromtimestamp(photo['date'])
                month = str(photo_date.month) if photo_date.month > 9 else "0" + str(photo_date.month)
                day = str(photo_date.day) if photo_date.day > 9 else "0" + str(photo_date.day)
                file_name = str(photo['likes']['count']) + "_" + day + month + str(photo_date.year)
                return file_name + ".jpg"
        return str(photo['likes']['count']) + ".jpg"

    def get_photos(self):
        return requests.get("https://api.vk.com/method/photos.get?owneer_id=" + self.vk_id
                            + "&album_id=profile&extended=1&access_token=" + self.access_token + "&v=5.122").json()

    def backup_photos(self, uploader):
        output_date = []
        photos = self.get_photos()['response']['items']
        total_photos = self.get_photos()['response']['count']
        for counter, photo in enumerate(photos):
            print(f"\nProcessing {counter + 1} photo out of {total_photos}")
            file_name = self.set_photo_name(output_date, photo)
            output_date.append({"file_name": file_name, "size": photo['sizes'][-1]['type']})
            uploader.upload(file_name, photo['sizes'][-1]['url'])
        with open(self.vk_id + "_photos.json", "w") as file:
            json.dump(output_date, file)


def main():
    print("Введите yandex token:")
    uploader_photos = YaUploader(input())
    print("Введите vk token:")
    vk_backup = VkBackup(input())
    vk_backup.backup_photos(uploader_photos)


main()
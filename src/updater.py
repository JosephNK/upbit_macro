from pprint import pprint
from src.helper import Helper
import os
import json
import emoji

kVer = "1.1.0"

class Updater:
    save_dir = 'config'
    file_name = 'version.json'
    file_path_name = f'{save_dir}/{file_name}'

    helper = Helper()

    def __init__(self):
        pass

    def is_exist_file(self):
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

        return os.path.isfile(self.file_path_name)

    def check(self):
        json_data = None

        if self.is_exist_file():
            with open(self.file_path_name, 'r') as f:
                json_data = json.load(f)
        
        if json_data == None:
            json_data = {
                'Version': kVer,
            }
            with open(self.file_path_name, 'w') as f:
                json.dump(json_data, f)

        current_ver = self.helper.safe_get(json_data, 'Version')
        if current_ver != kVer:
            return False
        return True
    
    def run(self):
        if not self.check():
            pprint(emoji.emojize(':beer_mug: 최신 소스로 업데이트를 진행 합니다.'))
            os.system('git pull')
            json_data = {
                'Version': kVer,
            }
            with open(self.file_path_name, 'w') as f:
                json.dump(json_data, f)
            pprint(emoji.emojize(':beer_mug: 업데이트가 완료 되었습니다.'))
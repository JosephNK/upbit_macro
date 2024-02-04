from prompt_toolkit import prompt
import os
import json

class KeyFile:
    save_dir = 'config'
    file_name = 'key.json'
    file_path_name = f'{save_dir}/{file_name}'

    def is_exist_file(self):
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

        return os.path.isfile(self.file_path_name)

    def read(self):
        with open(self.file_path_name, 'r') as f:
            json_data = json.load(f)
        return json_data
    
    def save(self):
        answer_access_key = prompt('1. AccessKey 키를 입력 하세요: ')
        answer_secret_key = prompt('2. SecretKey 키를 입력 하세요: ')
        json_data = {
            'AccessKey': answer_access_key,
            'SecretKey': answer_secret_key,
        }
        with open(self.file_path_name, 'w') as f:
            json.dump(json_data, f)
        return True
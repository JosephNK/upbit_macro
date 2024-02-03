from prompt_toolkit import prompt
import json

class KeyFile:
    def read(self, file_name):
        with open(file_name, 'r') as f:
            json_data = json.load(f)
        return json_data
    
    def save(self, file_name):
        answer_access_key = prompt('1. AccessKey 키를 입력 하세요: ')
        answer_secret_key = prompt('2. SecretKey 키를 입력 하세요: ')
        json_data = {
            'AccessKey': answer_access_key,
            'SecretKey': answer_secret_key,
        }
        with open(file_name, 'w') as f:
            json.dump(json_data, f)
        return True
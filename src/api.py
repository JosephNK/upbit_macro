from src.market_data_helper import MarketDataHelper
from urllib.parse import urlencode, unquote
import jwt 
import hashlib
import uuid
import requests
import json

class APIError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg

class API:
    server_url = 'https://api.upbit.com'
    default_json_headers = {"accept": "application/json"}
    authorization = ''

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.authorization = self.getAuthorization()

    def getAuthorization(self):
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        return authorization

    def getAuthorizationHeaders(self):
        headers = {
            'Authorization': self.authorization,
        }
        return headers

    def requestMyAccountList(self):
        headers = self.getAuthorizationHeaders()
        res = requests.get(self.server_url + '/v1/accounts', params={}, headers=headers)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        if (type(json_object) is list) == False:
            error = json_object.get('error', None)
            error_name = error.get('name', '')
            error_message = error.get('message', '')
            raise APIError(msg=f'{error_name} {error_message}')
        
        return MarketDataHelper().getMyAccountMarketList(json_object)

    def requestAllMarketList(self):
        res = requests.get(self.server_url + '/v1/market/all?isDetails=false', headers=self.default_json_headers)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        if (type(json_object) is list) == False:
            error = json_object.get('error', None)
            error_name = error.get('name', '')
            error_message = error.get('message', '')
            raise APIError(msg=f'{error_name} {error_message}')
        
        return json_object

    async def requestMarketTickerList(self, markets):
        res = requests.get(self.server_url + '/v1/ticker', headers=self.default_json_headers, params={'markets': markets})
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        if (type(json_object) is list) == False:
            error = json_object.get('error', '')
            error_name = error.get('name', '')
            error_message = error.get('message', '')
            raise APIError(msg=f'{error_name} {error_message}')

        return json_object
    
    async def requestMarketOrder(self, params):
        print(params)
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        self.authorization = self.getAuthorization()
        headers = self.getAuthorizationHeaders()
        headers['query_hash'] = query_hash
        headers['query_hash_alg'] = 'SHA512'
        
        res = requests.post(self.server_url + '/v1/orders', headers=headers, data=params)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        if (type(json_object) is list) == False:
            error = json_object.get('error', '')
            error_name = error.get('name', '')
            error_message = error.get('message', '')
            raise APIError(msg=f'{error_name} {error_message}')

        return json_object
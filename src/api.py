from src.helper import Helper
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

    helper = Helper()
    
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def getAuthorization(self):
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        return 'Bearer {}'.format(jwt_token)
    
    def getAuthorizationWithParams(self, params):
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret_key)
        return 'Bearer {}'.format(jwt_token)

    def getHeadersWithAuthorization(self, authorization):
        headers = {
            'Authorization': authorization,
        }
        return headers
    
    def getError(self, json):
        if (type(json) is list) == False:
            if self.helper.safe_get(json, 'error') != None:
                error = json.get('error', '')
                error_name = self.helper.safe_get(error, 'name')
                error_message = self.helper.safe_get(error, 'message')
                if error_name == None: error_name = ''
                if error_message == None: error_message = ''
                return APIError(msg=f'{error_name} {error_message}')
        return None

    def requestMyAccountList(self):
        authorization = self.getAuthorization()
        headers = self.getHeadersWithAuthorization(authorization=authorization)
        res = requests.get(self.server_url + '/v1/accounts', params={}, headers=headers)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        error_object = self.getError(json=json_object)
        if error_object != None:
            raise error_object
        
        return MarketDataHelper().getMyAccountMarketList(json_object)

    def requestAllMarketList(self):
        res = requests.get(self.server_url + '/v1/market/all?isDetails=false', headers=self.default_json_headers)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        error_object = self.getError(json=json_object)
        if error_object != None:
            raise error_object
        
        return json_object

    async def requestMarketTickerList(self, markets):
        res = requests.get(self.server_url + '/v1/ticker', headers=self.default_json_headers, params={'markets': markets})
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        error_object = self.getError(json=json_object)
        if error_object != None:
            raise error_object

        return json_object
    
    async def requestMarketOrder(self, params):
        authorization = self.getAuthorizationWithParams(params=params)
        headers = self.getHeadersWithAuthorization(authorization=authorization)
        res = requests.post(self.server_url + '/v1/orders', headers=headers, json=params)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        error_object = self.getError(json=json_object)
        if error_object != None:
            raise error_object

        return json_object
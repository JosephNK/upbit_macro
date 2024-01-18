# pip3 install PyJWT, requests, pyfiglet, inquirer, prompt_toolkit, click, PrettyTable

from pyfiglet import Figlet
from prompt_toolkit import prompt
from prettytable import PrettyTable
from urllib.parse import urlencode, unquote
from pprint import pprint
import inquirer
import jwt 
import uuid
import json
import hashlib
import os
import requests
import asyncio
import emoji
import click

class DataHelper:
    def getMyAccountMarketList(self, items):
        def innerMap(obj):
            currency = obj['currency']
            unit_currency = obj['unit_currency']
            market = unit_currency + '-' + currency
            obj['market'] = market
            return obj
        json_object = list(map(innerMap , items))
        return json_object

    def getNoHaveListFromCompare(self):
        def filterMarketItem(market_item):
            market = market_item['market']
            for my_item in my_account_items:
                my_market = my_item['market']
                if market == my_market:
                    return market_item
            return None
        json_object = list(filter(lambda x: x is not None, list(filter(filterMarketItem, all_market_items))))
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)
        return json_object

# API

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
        return DataHelper().getMyAccountMarketList(json_object)

    def requestAllMarketList(self):
        res = requests.get(self.server_url + '/v1/market/all?isDetails=false', headers=self.default_json_headers)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        return json_object

    async def requestMarketTickerList(self, markets):
        res = requests.get(self.server_url + '/v1/ticker', headers=self.default_json_headers, params={'markets': markets})
        json_object = res.json()
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)
        return json_object
        

# KeyFile

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

# Main

if __name__ == '__main__':
    # Welcome Message
    f = Figlet(font='slant')
    print(f.renderText('Upbit Mecro'))

    # Check Data.json

    file_name = 'data.json'

    if os.path.isfile(file_name):
        questions = [
            inquirer.List('key',
                            message="기존 키를 사용하시겠습니까?",
                            choices=['진행', '초기화'],
                        ),
        ]
        answers = inquirer.prompt(questions)
        value = answers['key']
        if value == '초기화':
            pprint(emoji.emojize(':beer_mug: 키를 새로 입력하세요.'))
            KeyFile().save(file_name=file_name)
    else:
        pprint(emoji.emojize(':beer_mug: 저장된 키가 없습니다.'))
        KeyFile().save(file_name=file_name)

    json_data = KeyFile().read(file_name=file_name)
    access_key_data = json_data['AccessKey']
    secret_key_data = json_data['SecretKey']

    # # Select 
    # questions = [
    # inquirer.List('size',
    #                 message="What size do you need?",
    #                 choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
    #             ),
    # ]
    # answers = inquirer.prompt(questions)
    # print(answers)

    api = API(access_key=access_key_data, secret_key=secret_key_data)
    all_market_items = api.requestAllMarketList()
    my_account_items = api.requestMyAccountList()

    async def custom_coroutine():
        no_have_my_market_items = list(filter(lambda x: x['market'] != 'KRW-KRW' and x['market'] != 'KRW-XCORE', my_account_items))
        no_have_my_market_symbol_items = list(map(lambda x: x['market'], no_have_my_market_items))
        ticker_items = await api.requestMarketTickerList(markets=no_have_my_market_symbol_items)

        def ticker_items_rebuild():
            for market_item in all_market_items:
                market_symbol = market_item['market']
                market_korean_name = market_item['korean_name']
                market_english_name = market_item['english_name']
                for ticker_item in ticker_items:
                    ticker_symbol = ticker_item['market']
                    if market_symbol == ticker_symbol:
                        ticker_item['korean_name'] = market_korean_name
                        ticker_item['english_name'] = market_english_name
        
        ticker_items_rebuild()

        x = PrettyTable()
        x.field_names = ["Market", "이름", "ChnagePrice"]

        for ticker_item in ticker_items:
            market = ticker_item['market']
            korean_name = ticker_item['korean_name']
            change_price = ticker_item['change_price']
            item = [market, korean_name, change_price]
            x.add_row(item)
        
        print(x)

    # async def async_generator(my_account_items):
    #     for my_account_item in my_account_items:
    #         await asyncio.sleep(2)
    #         market = my_account_item['market']
    #         print(market)
    #         yield await requestMarketTickerList([market])

    # async def custom_coroutine():
    #     # asynchronous for loop
    #     async for item in async_generator(my_account_items):
    #         # report the result
    #         print(item)

    asyncio.run(custom_coroutine())


# # no_have_items = getNoHaveListFromCompare()

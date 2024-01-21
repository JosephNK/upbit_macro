# pip3 install PyJWT requests pyfiglet inquirer prompt_toolkit click PrettyTable emoji

from pyfiglet import Figlet
from prompt_toolkit import prompt
from prettytable import PrettyTable
from urllib.parse import urlencode, unquote
from pprint import pprint
from datetime import datetime
from enum import Enum
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

class DataSort(Enum):
    NAME = 1
    RATE = 2

# MarketDataHelper

class MarketDataHelper:
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
        return MarketDataHelper().getMyAccountMarketList(json_object)

    def requestAllMarketList(self):
        res = requests.get(self.server_url + '/v1/market/all?isDetails=false', headers=self.default_json_headers)
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
        return json_object

    async def requestMarketTickerList(self, markets):
        res = requests.get(self.server_url + '/v1/ticker', headers=self.default_json_headers, params={'markets': markets})
        json_object = res.json()
        # json_formatted_str = json.dumps(json_object, indent=2)
        # print(json_formatted_str)
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
    
# ResultMyAccount

class MyCoinAccount:
    def __init__(self, api: API, is_have_market: bool):
        self.api = api
        self.is_have_market = is_have_market

    def run(self, all_market_items: list, my_account_items: list):
        return asyncio.run(self.custom_coroutine(all_market_items=all_market_items, my_account_items=my_account_items))

    async def custom_coroutine(self, all_market_items: list, my_account_items: list):
        allow_my_market_items = list(filter(lambda x: x['market'] != 'KRW-KRW' and x['market'] != 'KRW-XCORE', my_account_items))

        if self.is_have_market == True:
            market_items = allow_my_market_items
            market_symbol_items = list(map(lambda x: x['market'], market_items))
        else:
            def no_have_filter(all_market_item):
                market = all_market_item['market']
                for my_account_item in allow_my_market_items:
                    my_market = my_account_item['market']
                    if market == my_market:
                        return False
                return True
            market_items = list(filter(no_have_filter, all_market_items))
            market_items = list(filter(lambda x: 'KRW' in x['market'], market_items))
            market_symbol_items = list(map(lambda x: x['market'], market_items))

        ticker_items = await self.api.requestMarketTickerList(markets=market_symbol_items)

        def ticker_items_rebuild():
            new_ticker_items = []
            for all_market_item in all_market_items:
                market_symbol = all_market_item['market']
                market_korean_name = all_market_item['korean_name']
                market_english_name = all_market_item['english_name']
                for ticker_item in ticker_items:
                    ticker_symbol = ticker_item['market']
                    if market_symbol == ticker_symbol:
                        ticker_item['korean_name'] = market_korean_name
                        ticker_item['english_name'] = market_english_name
                        for have_my_market_item in market_items:
                            have_my_market_symbol = have_my_market_item['market']
                            if ticker_symbol == have_my_market_symbol:
                                new_ticker_item = ticker_item | have_my_market_item
                                new_ticker_items.append(new_ticker_item)
                                continue
            return new_ticker_items
        
        new_ticker_items = ticker_items_rebuild()

        return new_ticker_items

# ExcelTable            

class ExcelTable:
    table: PrettyTable

    def __init__(self, sort: DataSort):
        self.sort = sort
    
    def print(self, all_market_items: list, ticker_items: list):
        x = PrettyTable()
        x.field_names = ["Market", "이름", "현재가", "평균 매수가", "수익률(%)", "고가", "저가", "52주 신고가"]

        for ticker_item in ticker_items:
            market = ticker_item.get('market')
            # english_name = ticker_item.get('english_name')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = ticker_item.get('avg_buy_price', '0') # 평균 매수가
            # unit_currency = ticker_item.get('unit_currency')
            trade_price = ticker_item.get('trade_price', '0') # 현재가
            high_price = ticker_item.get('high_price', '0') # 고가
            low_price = ticker_item.get('low_price', '0') # 저가
            highest_52_week_price = ticker_item.get('highest_52_week_price', '0') # 52주 신고가

            f_avg_buy_price = float(avg_buy_price)
            f_trade_price = float(trade_price)
            f_high_price = float(high_price)
            f_low_price = float(low_price)

            avg_buy_price = '{0:,}'.format(f_avg_buy_price)
            trade_price = '{0:,}'.format(float(f_trade_price))
            high_price = '{0:,}'.format(float(f_high_price))
            low_price = '{0:,}'.format(float(f_low_price))
            highest_52_week_price = '{0:,}'.format(float(highest_52_week_price))

            # 수익률
            try:
                rate_of_return = round(((f_trade_price - f_avg_buy_price) / f_avg_buy_price) * 100, 2)
            except:
                rate_of_return = 0
                
            item = [market, 
                    korean_name, 
                    trade_price, 
                    avg_buy_price, 
                    rate_of_return, 
                    high_price,
                    low_price,
                    highest_52_week_price]
            x.add_row(item)

        if self.sort == DataSort.NAME:
            x.sortby = "이름"
        elif self.sort == DataSort.RATE:
            x.sortby = "수익률(%)"
            x.reversesort = True

        self.table = x
        print(x)

        all_krw_market_items = list(filter(lambda x: 'KRW' in x['market'], all_market_items))

        print(f'Total: {len(ticker_items)} / {len(all_krw_market_items)}')

    def save_excel(self):
        csv_file_name = str(datetime.now())
        with open(f'{csv_file_name}.csv', 'w', newline='') as f_output:
            f_output.write(self.table.get_csv_string())
            pprint(emoji.emojize(f':beer_mug: {csv_file_name}.csv 파일이 생성 되었습니다.'))

# Main

if __name__ == '__main__':
    # Welcome Message
    f = Figlet(font='slant')
    print(f.renderText('Upbit Mecro'))

    # Check Data.json

    file_name = 'data.json'

    if os.path.isfile(file_name):
        # Select 
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

    # API
    api = API(access_key=access_key_data, secret_key=secret_key_data)
    all_market_items = api.requestAllMarketList()
    my_account_items = api.requestMyAccountList()

    # Select 
    questions_func = [
        inquirer.List('func',
                        message="다음 중 원하는 기능을 선택하세요",
                        choices=['(A) 현재 자산의 리스트를 보시겠습니까?', 
                                '(B) 가지고 있는 않은 코인의 리스트를 보시겠습니까?'],
                    ),
    ]
    answers_func = inquirer.prompt(questions_func)
    func_value = answers_func['func']

    # Select 
    questions_sort = [
        inquirer.List('sort',
                    message="데이타 정렬을 선택하세요",
                    choices=['(A) 이름순', '(B) 수익율순'],
                ),
    ]
    answers_sort = inquirer.prompt(questions_sort)
    sort_value = answers_sort['sort']

    if "(A)" in func_value:
        is_have_market = True
    elif "(B)" in func_value:
        is_have_market = False

    if "(A)" in sort_value:
        data_sort = DataSort.NAME
    elif "(B)" in sort_value:
        data_sort = DataSort.RATE
    
    my_account = MyCoinAccount(api=api, is_have_market=is_have_market)
    ticker_items = my_account.run(all_market_items=all_market_items, my_account_items=my_account_items)

    execel_table = ExcelTable(sort=data_sort)
    execel_table.print(all_market_items=all_market_items, ticker_items=ticker_items)
    execel_table.save_excel()
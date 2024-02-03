# pip3 install PyJWT requests pyfiglet inquirer prompt_toolkit click PrettyTable emoji

from pyfiglet import Figlet
from pprint import pprint
from src.types import DataSort
from src.my_coin_account import MyCoinAccount
from src.order import UpbitOrder
from src.market_data_helper import MarketDataHelper
from src.key_file import KeyFile
from src.api import API, APIError
from src.excel_table import ExcelTable
import inquirer
import os
import sys
import emoji

file_name = 'data.json'

if __name__ == '__main__':
    # Welcome Message
    f = Figlet(font='slant')
    print(f.renderText('Upbit Mecro'))

    # Check Data.json
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
    try:
        api = API(access_key=access_key_data, secret_key=secret_key_data)
        all_market_items = api.requestAllMarketList()
        my_account_items = api.requestMyAccountList()
    except APIError as e:
        print(f'ERROR Reason :: {e}')
        sys.exit(0)
    
    # Select 
    questions_func = [
        inquirer.List('func',
                        message="다음 중 원하는 기능을 선택하세요",
                        choices=['(A) 현재 자산의 리스트를 보시겠습니까?', 
                                '(B) 가지고 있는 않은 코인의 리스트를 보시겠습니까?',
                                '(C) 매수 프로그램을 실행하시겠습니까?'],
                    ),
    ]
    answers_func = inquirer.prompt(questions_func)
    func_value = answers_func['func']

    if "(A)" in func_value:
        func_type_value = 'A'
        is_have_market = True
    elif "(B)" in func_value:
        func_type_value = 'B'
        is_have_market = False
    elif "(C)" in func_value:
        func_type_value = 'C'
        is_have_market = True

    data_sort = DataSort.NAME

    is_need_sort = (func_type_value == 'A' or func_type_value == 'B')

    if is_need_sort == True:
        # Select 
        questions_sort = [
            inquirer.List('sort',
                        message="데이타 정렬을 선택하세요",
                        choices=['(A) 이름순', '(B) 수익율순'],
                    ),
        ]
        answers_sort = inquirer.prompt(questions_sort)
        sort_value = answers_sort['sort']

        if "(A)" in sort_value:
            data_sort = DataSort.NAME
        elif "(B)" in sort_value:
            data_sort = DataSort.RATE
    
    try:
        my_account = MyCoinAccount(api=api, is_have_market=is_have_market)
        ticker_items = my_account.run(all_market_items=all_market_items, my_account_items=my_account_items)
        
        market_data_helper = MarketDataHelper()

        if is_need_sort == True:
            ticker_items = market_data_helper.getTickerItems(ticker_items=ticker_items, sort=DataSort.NAME)
            execel_table = ExcelTable(sort=data_sort)
            execel_table.print(all_market_items=all_market_items, ticker_items=ticker_items)
            execel_table.save_excel()
            
        if func_type_value == 'C':
            ticker_items = market_data_helper.getTickerItems(ticker_items=ticker_items, sort=DataSort.RATE)
            buy_coins = market_data_helper.getChoiceItems(ticker_items=ticker_items)

            # Select 
            questions_buy = [
                inquirer.Checkbox('buy',
                            message="구매 할 코인을 선택하세요. (마켓명 | 현재가 | 평균매수가 | 수익률 | 이름)",
                            choices=buy_coins,
                        ),
            ]
            answers_buys = inquirer.prompt(questions_buy)
            buy_strings = answers_buys['buy']

            if len(buy_strings) == 0:
                sys.exit(0)

            buy_value = input("코인당 매수가를 입력하세요. (ex., 100000) : ")
            
            if buy_value.rstrip() == '':
                sys.exit(0)
                
            total_buy_value = len(buy_strings) * int(buy_value)
            total_buy_value = '{0:,}'.format(total_buy_value)
            print(f'총 필요한 금액은 {total_buy_value} 입니다.\n')

            # Select 
            questions_ing = [
                inquirer.List('ing',
                            message="진행 하시겠습니까?",
                            choices=['(A) 진행', '(B) 중단'],
                        ),
            ]
            answers_ing = inquirer.prompt(questions_ing)
            ing_value = answers_ing['ing']

            if "(A)" in ing_value:
                upbit_order =  UpbitOrder(api=api)
                buy_items = []
                for buy_string in buy_strings:
                    select_market = buy_string.split('|')[0].rstrip()
                    data = {
                        'market': select_market,
                        'side': 'bid',
                        'ord_type': 'price',
                        'price': buy_value,
                        # 'volume': Null,
                    }
                    buy_items.append(data)
                upbit_order.buy_run(buy_items=buy_items)
            elif "(B)" in ing_value:
                sys.exit(0)
            
    except APIError as e:
        print(f'ERROR Reason :: {e}')
        sys.exit(0)
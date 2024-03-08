# pip3 install PyJWT requests pyfiglet inquirer prompt_toolkit click PrettyTable emoji

from pyfiglet import Figlet
from pprint import pprint
from src.data_types import DataSort
from src.my_coin_account import MyCoinAccount
from src.order import UpbitOrder
from src.key_file import KeyFile
from src.updater import Updater
from src.api import API, APIError
from src.excel_table import ExcelTable
import inquirer
import sys
import emoji

if __name__ == '__main__':
    # Welcome Message
    f = Figlet(font='slant')
    print(f.renderText('Upbit Mecro'))

    # Check Updater
    updater = Updater()
    updater.run()

    # Check Data.json
    key_file = KeyFile()
    if key_file.is_exist_file():
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
            key_file.save()
    else:
        pprint(emoji.emojize(':beer_mug: 저장된 키가 없습니다.'))
        key_file.save()
    json_data = key_file.read()
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
                                '(C) ----------------------------------',
                                '(D) 매수 프로그램을 실행하시겠습니까?'],
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
    elif "(D)" in func_value:
        func_type_value = 'D'
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
        # MyCoinAccount
        my_account = MyCoinAccount(api=api, is_have_market=is_have_market)
        ticker_items = my_account.run(all_market_items=all_market_items, my_account_items=my_account_items)
        
        if is_need_sort == True:
            # ExcelTable
            execel_table = ExcelTable(sort=data_sort, origin_ticker_items=ticker_items)
            execel_table.print(all_market_items=all_market_items)
            execel_table.save_excel()

        if func_type_value == 'C':
            print('Not implemented')

        if func_type_value == 'D':
            # UpbitOrder
            upbit_order = UpbitOrder(api=api, origin_ticker_items=ticker_items, my_account_items=my_account_items)
            upbit_order.process()
            
    except APIError as e:
        print(f'ERROR Reason :: {e}')
        sys.exit(0)
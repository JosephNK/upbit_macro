from pprint import pprint
from src.api import API, APIError
from src.market_data_helper import MarketDataHelper
from src.data_types import DataSort
import inquirer
import sys
import emoji
import asyncio

class UpbitOrder:
    ticker_items: list
    buy_coins: list

    market_data_helper = MarketDataHelper()

    def __init__(self, api: API, origin_ticker_items: list):
        self.api = api
        self.ticker_items = self.market_data_helper.getTickerItems(ticker_items=origin_ticker_items, sort=DataSort.RATE)
        self.buy_coins = self.market_data_helper.getChoiceItems(ticker_items=self.ticker_items)

    def process(self):
         # Select 
        questions_buy = [
            inquirer.Checkbox('buy',
                        message="구매 할 코인을 선택하세요. (마켓명 | 현재가 | 매수평균가 | 평가금액 | 수익률 | 이름)",
                        choices=self.buy_coins,
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
            self.buy_run(buy_items=buy_items)
        elif "(B)" in ing_value:
            sys.exit(0)

    def buy_run(self, buy_items: list):
        if len(buy_items) > 0:
            pprint(emoji.emojize(':beer_mug: 설정한 금액으로 매수를 진행 합니다. (시장가)'))

        for buy_item in buy_items:
            asyncio.run(self.buy_custom_coroutine(data=buy_item))

        if len(buy_items) > 0:
            pprint(emoji.emojize(':beer_mug: 매수를 진행이 완료 되었습니다.'))
            
    async def buy_custom_coroutine(self, data):
        market = data['market']
        await asyncio.sleep(1)
        try:
            order_item = await self.api.requestMarketOrder(params=data)
            pprint(emoji.emojize(f':beer_mug: {market} 매수 신청 완료 되었습니다.'))
        except APIError as e:
            raise e
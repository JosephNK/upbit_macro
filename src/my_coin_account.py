from src.api import API, APIError
import asyncio

class MyCoinAccount:
    def __init__(self, api: API, is_have_market: bool):
        self.api = api
        self.is_have_market = is_have_market

    def run(self, all_market_items: list, my_account_items: list):
        return asyncio.run(self.custom_coroutine(all_market_items=all_market_items, my_account_items=my_account_items))

    async def custom_coroutine(self, all_market_items: list, my_account_items: list):
        allow_my_market_items = list(filter(lambda x: not (x['market'] == 'KRW-KRW' or x['avg_buy_price'] == '0') , my_account_items))

        if self.is_have_market == True:
            market_items = allow_my_market_items
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

        if len(market_symbol_items) == 0:
            return []

        try:
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
        except APIError as e:
            raise e
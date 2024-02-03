from src.api import API, APIError
import asyncio

class UpbitOrder:
    def __init__(self, api: API):
        self.api = api

    def buy_run(self, buy_items: list):
        for buy_item in buy_items:
            asyncio.run(self.buy_custom_coroutine(data=buy_item))
            

    async def buy_custom_coroutine(self, data):
        market = data['market']
        await asyncio.sleep(1)
        try:
            order_item = await self.api.requestMarketOrder(data=data)
            print(f'{market} 매수 신청 완료 되었습니다.')
        except APIError as e:
            raise e
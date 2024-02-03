from src.types import DataSort
import json

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

    def getNoHaveListFromCompare(self, all_market_items: list, my_account_items: list):
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
    
    def getTickerItems(self, ticker_items: list, sort: DataSort):
        items = []

        for ticker_item in ticker_items:
            market = ticker_item.get('market')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = ticker_item.get('avg_buy_price', '0') # 평균 매수가
            trade_price = ticker_item.get('trade_price', '0') # 현재가
            high_price = ticker_item.get('high_price', '0') # 고가
            low_price = ticker_item.get('low_price', '0') # 저가
            highest_52_week_price = ticker_item.get('highest_52_week_price', '0') # 52주 신고가

            f_avg_buy_price = round(float(avg_buy_price), 2)
            f_trade_price = round(float(trade_price), 2)
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

            item = {
                'market': market,
                'korean_name': korean_name,
                'trade_price': trade_price,
                'avg_buy_price': avg_buy_price,
                'rate_of_return': rate_of_return,
                'high_price': high_price,
                'low_price': low_price,
                'highest_52_week_price': highest_52_week_price,
            }

            items.append(item)

        if sort == DataSort.NAME:
            items = sorted(items, key=lambda d: d['korean_name']) 
        elif sort == DataSort.RATE:
            items = sorted(items, key=lambda d: d['rate_of_return'], reverse=True) 

        return items
    
    def getChoiceItems(self, ticker_items: list):
        items = []

        for ticker_item in ticker_items:
            market = ticker_item.get('market').ljust(15, ' ')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = str(ticker_item.get('avg_buy_price', '0')).ljust(15, ' ') # 평균 매수가
            trade_price = str(ticker_item.get('trade_price', '0')).ljust(15, ' ') # 현재가
            rate_of_return = str(ticker_item.get('rate_of_return', '0')).ljust(8, ' ') # 수익율

            items.append(f'{market}| {trade_price}| {avg_buy_price}| {rate_of_return}| {korean_name}')

        return items

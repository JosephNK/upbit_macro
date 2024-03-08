from src.data_types import DataSort
import math
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
    
    def getMyCurrentPrice(self, my_account_items: list):
        krw_market_items = list(filter(lambda x: (x['market'] == 'KRW-KRW') , my_account_items))
        if len(krw_market_items) > 0:
            current_price = krw_market_items[0]['balance']
            f_current_price = round(float(current_price), 2)
            return f_current_price
        return 0
    
    def getAllowMyMarketItems(self, my_account_items: list):
        allow_my_market_items = list(filter(lambda x: not (x['market'] == 'KRW-KRW' or x['avg_buy_price'] == '0') , my_account_items))
        return allow_my_market_items

    def getTickerItems(self, ticker_items: list, sort: DataSort):
        items = []

        for ticker_item in ticker_items:
            market = ticker_item.get('market')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = ticker_item.get('avg_buy_price', '0') # 매수평균가
            balance = ticker_item.get('balance', '0')
            locked = ticker_item.get('locked', '0')
            trade_price = ticker_item.get('trade_price', '0') # 현재가
            high_price = ticker_item.get('high_price', '0') # 고가
            low_price = ticker_item.get('low_price', '0') # 저가
            highest_52_week_price = ticker_item.get('highest_52_week_price', '0') # 52주 신고가
            lowest_52_week_price = ticker_item.get('lowest_52_week_price', '0') # 52주 신저가

            f_avg_buy_price = round(float(avg_buy_price), 2)
            f_locked = round(float(locked), 2)
            f_trade_price = round(float(trade_price), 2)
            f_evaluation_price = math.trunc(round(float(trade_price) * float(balance), 2)) # 평가 금액
            f_buy_price = math.trunc(round(float(avg_buy_price) * float(balance), 2)) # 매수 금액
            f_high_price = float(high_price)
            f_low_price = float(low_price)

            avg_buy_price = '{0:,}'.format(f_avg_buy_price)
            locked = '{0:,}'.format(f_locked)
            trade_price = '{0:,}'.format(float(f_trade_price))
            evaluation_price = '{0:,}'.format(float(f_evaluation_price))
            buy_price = '{0:,}'.format(float(f_buy_price))
            high_price = '{0:,}'.format(float(f_high_price))
            low_price = '{0:,}'.format(float(f_low_price))
            highest_52_week_price = '{0:,}'.format(float(highest_52_week_price))
            lowest_52_week_price = '{0:,}'.format(float(lowest_52_week_price))

            # 수익률
            try:
                rate_of_return = round(((f_trade_price - f_avg_buy_price) / f_avg_buy_price) * 100, 2)
            except:
                rate_of_return = 0

            # 평가손익
            try:
                f_profit_loss_price = round(f_evaluation_price - f_buy_price, 2)
            except:
                f_profit_loss_price = 0

            profit_loss_price = '{0:,}'.format(float(f_profit_loss_price))

            item = {
                'market': market,
                'korean_name': korean_name,
                'trade_price': trade_price,
                'avg_buy_price': avg_buy_price,
                'locked': locked,
                'evaluation_price': evaluation_price,
                'buy_price': buy_price,
                'rate_of_return': rate_of_return,
                'high_price': high_price,
                'low_price': low_price,
                'profit_loss_price': profit_loss_price,
                'highest_52_week_price': highest_52_week_price,
                'lowest_52_week_price': lowest_52_week_price,
            }

            items.append(item)

        if sort == DataSort.NAME:
            items = sorted(items, key=lambda d: d['korean_name']) 
        elif sort == DataSort.RATE:
            items = sorted(items, key=lambda d: d['rate_of_return'], reverse=False) 

        return items
    
    def getChoiceItems(self, ticker_items: list):
        items = []

        for ticker_item in ticker_items:            
            market = ticker_item.get('market').ljust(15, ' ')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = str(ticker_item.get('avg_buy_price', '0')).ljust(15, ' ') # 매수평균가
            # evaluation_price = str(ticker_item.get('evaluation_price', '0')).ljust(15, ' ') # 평가금액
            buy_price = str(ticker_item.get('buy_price', '0')).ljust(15, ' ') # 매수금액
            trade_price = str(ticker_item.get('trade_price', '0')).ljust(15, ' ') # 현재가
            rate_of_return = str(ticker_item.get('rate_of_return', '0')).ljust(8, ' ') # 수익율
            profit_loss_price = str(ticker_item.get('profit_loss_price', '0')).ljust(8, ' ') # 평가손익

            items.append(f'{market}| {trade_price}| {avg_buy_price}| {buy_price}| {rate_of_return}| {korean_name}')

        return items

from prettytable import PrettyTable
from pprint import pprint
from datetime import datetime
from src.market_data_helper import MarketDataHelper
from src.data_types import DataSort
import os
import emoji

class ExcelTable:
    table: PrettyTable
    ticker_items: list

    market_data_helper = MarketDataHelper()

    def __init__(self, sort: DataSort, origin_ticker_items: list):
        self.sort = sort
        self.ticker_items = self.market_data_helper.getTickerItems(ticker_items=origin_ticker_items, sort=DataSort.NAME)
    
    def print(self, all_market_items: list):
        x = PrettyTable()
        x.field_names = ["Market", "이름", "현재가", "매수평균가", "평가금액", "평가손익", "수익률(%)", "고가", "저가", "52주 신고가"]

        for ticker_item in self.ticker_items:
            market = ticker_item.get('market')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = ticker_item.get('avg_buy_price', '0') # 매수평균가
            evaluation_price = ticker_item.get('evaluation_price', '0') # 평가금액
            trade_price = ticker_item.get('trade_price', '0') # 현재가
            high_price = ticker_item.get('high_price', '0') # 고가
            low_price = ticker_item.get('low_price', '0') # 저가
            rate_of_return = ticker_item.get('rate_of_return', '0') # 수익률
            profit_loss_price = ticker_item.get('profit_loss_price', '0') # 평가손익
            highest_52_week_price = ticker_item.get('highest_52_week_price', '0') # 52주 신고가

            item = [market, 
                    korean_name, 
                    trade_price, 
                    avg_buy_price, 
                    evaluation_price,
                    profit_loss_price,
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
        print(x) # 테이블 결과 출력

        all_krw_market_items = list(filter(lambda x: 'KRW' in x['market'], all_market_items))

        print(f'Total: {len(self.ticker_items)} / {len(all_krw_market_items)}') # Total 결과 출력

    def save_excel(self):
        save_dir = 'excel'
        csv_file_name = str(datetime.now())

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        
        with open(f'{save_dir}/{csv_file_name}.csv', 'w', newline='') as f_output:
            f_output.write(self.table.get_csv_string())
            pprint(emoji.emojize(f':beer_mug: {csv_file_name}.csv 파일이 생성 되었습니다.'))
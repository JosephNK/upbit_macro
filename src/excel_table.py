from prettytable import PrettyTable
from pprint import pprint
from datetime import datetime
from src.types import DataSort
import emoji

class ExcelTable:
    table: PrettyTable

    def __init__(self, sort: DataSort):
        self.sort = sort
    
    def print(self, all_market_items: list, ticker_items: list):
        x = PrettyTable()
        x.field_names = ["Market", "이름", "현재가", "평균 매수가", "수익률(%)", "고가", "저가", "52주 신고가"]

        for ticker_item in ticker_items:
            market = ticker_item.get('market')
            korean_name = ticker_item.get('korean_name')
            avg_buy_price = ticker_item.get('avg_buy_price', '0') # 평균 매수가
            trade_price = ticker_item.get('trade_price', '0') # 현재가
            high_price = ticker_item.get('high_price', '0') # 고가
            low_price = ticker_item.get('low_price', '0') # 저가
            rate_of_return = ticker_item.get('rate_of_return', '0') # 수익률
            highest_52_week_price = ticker_item.get('highest_52_week_price', '0') # 52주 신고가
                
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
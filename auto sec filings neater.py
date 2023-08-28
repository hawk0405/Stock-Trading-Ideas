import pandas as pd
import feedparser
import yfinance
import datetime
import requests
import json
import time

tickers_cik = requests.get('https://www.sec.gov/files/company_tickers.json','Hawk C secattempt0001@gmail.com').json()
TICKER_DF = pd.DataFrame(list(zip(list(map(lambda x: x['cik_str'], tickers_cik.values())),list(map(lambda x:x['ticker'], tickers_cik.values())))), columns = ['CIK','Ticker'])

def actual_trade(ticker:str,shares:int,assets:int,intangibles:int,liabilities:int,multiple:int): ## FEELS LIKE IT SHOULD BE IN A DIFFERENT PLACE NOT SURE EXACTLY HOW TO DO THAT ANYMORE
    bookvalue = (((assets-liabilities-intangibles)/shares)*multiple)
    if  bookvalue *.5 > get_price(ticker):
        print(ticker, 'BUY', bookvalue,'price',get_price(ticker))
    else:
        print(ticker,'not a buy', bookvalue,'price',get_price(ticker))

def get_100_filings():
    list_of_CIK = []
    try:
        d = feedparser.parse('https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=10&company=&dateb=&owner=include&start=0&count=100&output=atom',agent='Hawk C secattempt0001@gmail.com')
        for n in range(len(d['entries'])):
            full_name = d['entries'][n]['title']
            filing = str(full_name.split(' ')[0])
            CIK = full_name.split('(')[1].split(')')[0]
            if filing == '10-Q' or filing == '10-K':
                if str(d['entries'][n]['updated'].split('T')[0]) == str(datetime.datetime.now()).split(' ')[0]:
                    list_of_CIK.append(CIK)
    except:
        print('Issue Getting Filings')
    return list_of_CIK
                
def filings_in_progress(CIK_list:list):
    n = int(str(datetime.datetime.now()).split(' ')[1].split(':')[0])
    while n >= 6 and n <= 18:
        n = int(str(datetime.datetime.now()).split(' ')[1].split(':')[0])
        time.sleep(1)
        CIK_list = CIK_list + [x for x in get_100_filings() if x not in CIK_list]
    return CIK_list
        
def check_ticker_exists(CIK:int):
    if CIK in TICKER_DF['CIK'].to_list():
        return True
    else:
        return False

def check_yahoo_finance_ticker(ticker:str):
    if len(yfinance.Ticker(ticker).history(period='6mo')) > 0:
        return True
    else:
        return False

def check_sec_filing(CIK:str):
    if requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json',headers={'User-Agent':'secattempt0001@gmail.com'}).status_code == 200:
        return True
    else:
        return False

def find_ticker(CIK:int):
    return TICKER_DF[TICKER_DF['CIK'] == CIK].Ticker.values[0]

def get_json_file(CIK:str):
    return requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json',headers={'User-Agent':'secattempt0001@gmail.com'}).json()

def assets_exists(json_file:json):
    if 'Assets' in json_file['facts']['us-gaap']:
        return True
    else:
        return False

def get_assets(json_file:json):
        return json_file['facts']['us-gaap']['Assets']['units']['USD'][-1]['val']

def liabilities_exists(json_file:json):
    if 'Liabilities' in json_file['facts']['us-gaap']:
        return True
    else:
        return False

def get_liabilities(json_file:json):
    return json_file['facts']['us-gaap']['Liabilities']['units']['USD'][-1]['val']

def shares_exists(json_file:json):
    if 'WeightedAverageNumberOfDilutedSharesOutstanding' in json_file['facts']['us-gaap']:
        return True
    else:
        return False

def get_shares(json_file:json):
    return json_file['facts']['us-gaap']['WeightedAverageNumberOfDilutedSharesOutstanding']['units']['shares'][-1]['val']

def get_price(ticker:str):
    return yfinance.Ticker(ticker).history(period='6mo')['Close'][-1] 

def book_value(assets:int,liabilities:int,shares:int):
    return (assets-liabilities)/shares

BOUGHT_STOCKS = ['UFI']

def possible_run(bought_stocks = BOUGHT_STOCKS):
    CIK_list = filings_in_progress([])
    for CIK in CIK_list:
        time.sleep(1)
        if check_ticker_exists(int(CIK)) and check_sec_filing(CIK) and check_yahoo_finance_ticker(find_ticker(int(CIK))):
            json_file = get_json_file(CIK)
            if assets_exists(json_file) and liabilities_exists(json_file) and shares_exists(json_file):
                if book_value(int(get_assets(json_file)),int(get_liabilities(json_file)),int(get_shares(json_file)))*.5 > get_price(find_ticker(int(CIK))):
                    print('BUY',find_ticker(int(CIK)),CIK,'Book Value',book_value(get_assets(json_file),get_liabilities(json_file),get_shares(json_file)),'Actual Price',get_price(find_ticker(int(CIK))))

                elif book_value(int(get_assets(json_file)),int(get_liabilities(json_file)),int(get_shares(json_file))) <= get_price(find_ticker(int(CIK))) and find_ticker(int(CIK)) in bought_stocks:
                    print('SELL',find_ticker(int(CIK)),CIK,'Book Value',book_value(get_assets(json_file),get_liabilities(json_file),get_shares(json_file)),'Actual Price',get_price(find_ticker(int(CIK))))
            else:
                print(find_ticker(int(CIK)),'Something Does not Exist')

        elif find_ticker(int(CIK)) in bought_stocks:
            print(find_ticker(int(CIK)),'Currently Owned Should Look At')
            
        else:
            print(CIK, "This does not work because of price on yahoo finance or ticker does not exist or sec filing is weird")





















    
    






















                
    

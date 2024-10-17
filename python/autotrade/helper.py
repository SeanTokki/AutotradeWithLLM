import pyupbit
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
# from langchain_community.document_loaders import AsyncChromiumLoader
from bs4 import BeautifulSoup
import json

# import from my codes
from asset import AssetforTest
import crawler

def getRealtimeData():
    # get current orderbook
    orderbook = pyupbit.get_orderbook(ticker="KRW-BTC")
    del orderbook['level']
    current_time = datetime.fromtimestamp(orderbook['timestamp']//1000)  # remove millisecond time
    # current_time = current_time + timedelta(hours=9)  # UTC to KST
    current_time = str(current_time)  # dateTime obj to str
    del orderbook['timestamp']

    # get current asset information
    balances = AssetforTest.getBalances()  # balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == "BTC":
            btc_balance = b['balance']
            btc_avg_price = b['avg_buy_price']
        if b['currency'] == "KRW":
            krw_balance = b['balance']

    # gather data in one dictionary
    realtime_data = {'current_time': current_time, 'orderbook': orderbook, 'btc_balance': btc_balance,
                    'krw_balance': krw_balance, 'btc_avg_price': btc_avg_price}

    return realtime_data

def getHistoricalData():
    # get market data(OHLCV)
    df_daily = pyupbit.get_ohlcv("KRW-BTC", "day", count=60)
    df_hourly = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count=60)
    # df_fivemin = pyupbit.get_ohlcv("KRW-BTC", interval="minute5", count=60)

    # save last candle's close price as current btc price
    btc_price = df_hourly.iloc[-1].iloc[3]

    # helper function to arrange the dataset
    def arrangeDF(df):
        df = df.drop('value', axis=1)
        CustomStrategy = ta.Strategy(
            name="Strategy 1",
            description="EMA_10, RSI_14, StochRSI_14_14_3_3, MACD_12_26_9, BBands_20_2",
            ta=[
                {"kind": "ema", "length": 10},
                {"kind": "rsi", "length": 14},
                {"kind": "stochrsi", "length": 14, "rsi_length": 14, "k" : 3, "d" : 3},
                {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},
                {"kind": "bbands", "length" : 20, "std" : 2},
            ]
        )
        df.ta.cores = 0 # no multiprocessing
        df.ta.strategy(CustomStrategy)
        df = df.drop('MACDh_12_26_9', axis=1)
        df = df.drop('BBB_20_2.0', axis=1)
        df = df.drop('BBP_20_2.0', axis=1)
        df.index = df.index.strftime('%Y-%m-%d %T')

        return df[33:]

    # arange the datasets
    df_daily = arrangeDF(df_daily)
    df_hourly = arrangeDF(df_hourly)
    # df_fivemin = arrangeDF(df_fivemin)

    # gather the datasets in one dictionary
    historical_data = pd.concat([df_daily, df_hourly], keys=['daily', 'hourly'])
    historical_data = historical_data.to_dict(orient='split')

    return historical_data, btc_price

def _getCoinnessFastNews():
    html_text = crawler.fetchWithPlaywright(['https://coinness.com/'])

    soup = BeautifulSoup(html_text[0], 'html.parser')
    news = soup.select_one('main > div:nth-child(2) > div > div:nth-child(2)').get_text()

    return news

# Todo: click "암호화폐" button
def _getCoinnessNewsLinksTitles():
    html_text = crawler.fetchWithPlaywright(['https://coinness.com/article'])

    soup = BeautifulSoup(html_text[0], 'html.parser')
    # print(f"crawling 'a' elements...")
    elements = soup.find_all('a', {'target': '_blank'})
    
    links = []
    titles = []
    for element in elements:
        # print(f"finding url from {len(links)+1}th elements...")
        child_div_h3 = element.div.h3
        if child_div_h3 is not None:
            links.append(element.get('href'))
            titles.append(child_div_h3.get_text())
    
    return links, titles

def _getNewsByLinks(links):
    html_texts = crawler.asyncFetchWithPlaywright(links)
    # html_texts = [loadWithPlaywright(links[i]) for i in range(3)]

    news_list = []
    for html_text in html_texts:
        if html_text is None: 
            news_list.append(None)
            continue
        soup = BeautifulSoup(html_text, 'html.parser')
        news = soup.get_text().replace("\n", "")
        news_list.append(news)

    return news_list

def getCoinnessNews():
    fast_news = _getCoinnessFastNews()
    links, titles = _getCoinnessNewsLinksTitles()
    # Arrange two arrays simultaneously based on links
    links, titles = map(list, zip(*sorted(zip(links,titles))))
    news = _getNewsByLinks(links)
    news.append(fast_news)

    # Substitute empty news content to the news title
    for i in range(len(news)):
        if news[i] == "":
            news[i] = titles[i]
            # print(f"news {i}: {news[i]}")
        # else:
            # print(f"news {i}: {news[i][:100]}")
        
    return news

def readJSON(file_path):
    try:
        with open(file_path, "r") as file:
            content = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print("An error occurred while reading the file:", e)
        return None
    
    return content

def readFile(file_path):
  # read content from the file path
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print("An error occurred while reading the file:", e)
        return None

    return content

def checkFormat(res):
    # check if the response is dictionary
    if not isinstance(res, dict):
        return None

    # check if the decision is one of 'buy', 'sell', 'hold'
    if res.get('decision') not in ('buy', 'sell', 'hold'):
        return None

    # check if the ratio is a desired number
    ratio = res.get('ratio')
    if isinstance(ratio, str):
        try:
            float(ratio)
        except ValueError:
            return None
    elif isinstance(ratio, int):
        if ratio < 0 or ratio > 100:
            return None
        else:
            res['ratio'] = ratio * 0.01
            return res
    elif isinstance(ratio, float):
        if ratio < 0 or ratio > 1:
            return None
        else:
            return res
    else:
        return None

# Todo
def executeBuy(ratio):
    print(f"Buy with the ratio: {ratio}")

    return

# Todo
def executeSell(ratio):
    print(f"Sell with the ratio: {ratio}")

    return
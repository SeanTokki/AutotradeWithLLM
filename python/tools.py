import pyupbit
import pandas_ta as ta
from typing import Dict, List, Tuple, Literal, Annotated
from langchain_core.tools import tool
from langchain_community.tools import TavilySearchResults
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import crawler


@tool
def requestAgent(target_agent: Literal["chart_analyst", "news_analyst"], request: str):
    """
    Sending analysis request to a specified agent.
    Args:
        target_agent: the name of the agent. List of the available agents is as follows: [chart_analyst, news_analyst]
        request: the request content.
    """
    
    return

@tool
def getChartData(
    ticker: str,
    interval: Literal["minute5", "minute15", "minute60", "minute240", "day", "week", "month"],
    count: int
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Fetches chart data corresponding to given ticker, interval, count.
    Args:
        ticker: The ticker of the coin to look up.
        interval: The time interval of the candles to look up.
        count: Number of candles to look up. It should be an integer between 1 to 30.
    """

    # get market data(OHLCV)
    df = pyupbit.get_ohlcv(ticker, interval, count + 33)

    # helper function to arrange the dataset
    def arrangeDF(df):
        df = df.drop("value", axis=1)
        CustomStrategy = ta.Strategy(
            name="Strategy 1",
            description="EMA_10, RSI_14, StochRSI_14_14_3_3, MACD_12_26_9, BBands_20_2",
            ta=[
                {"kind": "ema", "length": 10},
                {"kind": "rsi", "length": 14},
                {"kind": "stochrsi", "length": 14, "rsi_length": 14, "k": 3, "d": 3},
                {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},
                {"kind": "bbands", "length": 20, "std": 2},
            ],
        )
        df.ta.cores = 0  # no multiprocessing
        df.ta.strategy(CustomStrategy)
        df = df.drop("MACDh_12_26_9", axis=1)
        df = df.drop("BBB_20_2.0", axis=1)
        df = df.drop("BBP_20_2.0", axis=1)
        df.index = df.index.strftime("%Y-%m-%d %T")

        return df[33:]

    # arange the datasets
    df = arrangeDF(df)

    # gather the datasets in one dictionary
    dict_data = df.to_dict("index")
    chart_data = {ticker: dict_data}

    return chart_data


def _getCoinnessNewsLinksTitles() -> Tuple[List[str], List[str]]:
    html_text = crawler.fetchWithPlaywright(["https://coinness.com/article"])

    soup = BeautifulSoup(html_text[0], "html.parser")
    elements = soup.find_all("a", {"target": "_blank"})

    links = []
    titles = []
    for element in elements:
        child_div_h3 = element.div.h3
        if child_div_h3 is not None:
            links.append(element.get("href"))
            titles.append(child_div_h3.get_text())

    return links, titles


def _getNewsByLinks(links: List[str]) -> List[str]:
    html_texts = crawler.asyncFetchWithPlaywright(links)

    news_list = []
    for html_text in html_texts:
        if html_text is None:
            news_list.append("")
            continue
        soup = BeautifulSoup(html_text, "html.parser")
        news = soup.get_text().replace("\n", "")
        news_list.append(news)

    return news_list


@tool
def getCoinnessNews() -> List[str]:
    """Get news related to cryptocurrency, crawled from https://coinness.com"""

    links, titles = _getCoinnessNewsLinksTitles()
    links, titles = map(list, zip(*sorted(zip(links, titles))))
    news = _getNewsByLinks(links)

    # Substitute empty news content to the news title
    for i in range(len(news)):
        if news[i] == "":
            news[i] = titles[i]

    return news


@tool
def webSearch(query: str) -> List[Dict[str, str]]:
    """
    Get web search results about query.
    Args:
        query: The query about what you want to know.
    """
    load_dotenv
    web_search = TavilySearchResults(max_results=3)
    results = web_search.invoke(query)

    return results
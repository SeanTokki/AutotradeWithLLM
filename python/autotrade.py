# import os
from dotenv import load_dotenv
import json

# import time
# import schedule
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnableLambda

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_core.pydantic_v1 import BaseModel, Field
# from typing import Union
# from datetime import datetime

# import from my codes
from asset import AssetforTest
from DB import Database as DB
import helper

# load environment
load_dotenv()


def prepareNews():
    # get list of news from "coinness.com"
    news = helper.getCoinnessNews()
    # with open('test.txt', 'r') as file_data:
    #     news = file_data.read()

    news_instructions = helper.readFile("./instructions/news_organize_instructions.md")

    news_template = ChatPromptTemplate.from_messages(
        [
            ("system", "Instruction: {news_instructions}"),
            ("human", "Input: {news}"),
        ]
    )

    return news, news_instructions, news_template


def prepareSystemPrompt():
    instructions = helper.readFile("./instructions/instructions.md")
    context = helper.readFile("./instructions/context.md")
    # ex_outputs = helper.readJSON("./instructions/examples.json")
    examples = [
        {
            "input1": '{"current_time": "2024-04-02 19:50:01", "orderbook": {...}, "btc_balance": 0.1, "krw_balance": 8000000, "btc_avg_price": 80000000}',
            "input2": '{"index": [["daily", "2024-03-07 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
            "output": '{"decision": "buy", "ratio": 50, "reason": "The recent historical data shows a positive trend with the 5-minute and hourly closing prices consistently above the EMA_10, indicating a strong upward momentum. The RSI_14 is currently at 45, which suggests that the market is not overbought yet. Additionally, the MACD line is above the signal line, further indicating a bullish trend. The order book reveals a strong support level at the current bid price with a significant volume of buy orders. Although recent news highlights regulatory and economic challenges, the overall sentiment remains positive due to Bitcoin perception as a hedge against inflation. Therefore, investing 50 percents of the available KRW balance in Bitcoin is a calculated risk, taking into account the upward trend and market support."}',
        },
        {
            "input1": '{"current_time": "2024-03-20 12:00:00", "orderbook": {...}, "btc_balance": 0.25, "krw_balance": 5000000, "btc_avg_price": 85000000}',
            "input2": '{"index": [["daily", "2024-02-23 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
            "output": '{"decision": "sell", "ratio": 30, "reason": "Current market analysis indicates that the RSI_14 is at 75, signaling an overbought condition which could lead to a price correction. The MACD has started to converge with the signal line, suggesting a potential bearish reversal. Additionally, the Bollinger Bands show the price is nearing the upper band, which often precedes a pullback. The latest news about regulatory uncertainties and economic challenges also adds to the bearish sentiment. Therefore, it is prudent to sell 30 percents of the current Bitcoin holdings to mitigate potential losses while still holding a majority position in case the trend resumes."}',
        },
        {
            "input1": '{"current_time": "2024-03-25 20:10:07", "orderbook": {...}, "btc_balance": 0.05, "krw_balance": 7500000, "btc_avg_price": 90000000}',
            "input2": '{"index": [["daily", "2024-02-28 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
            "output": '{"decision": "hold", "ratio": 100, "reason": "The historical market data presents a mixed scenario with the closing price hovering around the EMA_10 and the RSI_14 at a neutdevelopments and avoid potential risks."}',
        },
    ]

    return instructions, context, examples


def prepareData():
    real = helper.getRealtimeData()
    historical, btc_price = helper.getHistoricalData()
    realtime_data = json.dumps(real)
    historical_data = json.dumps(historical)

    # save current btc price for test
    AssetforTest.setBTCPrice(btc_price)

    # insert asset and price information into DB
    DB.insertIntoAsset(real, btc_price)

    # update the last recommendation's result based on current asset
    DB.updateRecommendationResult()

    return realtime_data, historical_data


def createTemplate(examples):
    # few-shot template
    example_prompt = ChatPromptTemplate.from_messages(
        [("human", "JSON Data 1: {input1}\nJSON Data 2: {input2}"), ("ai", "{output}")]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    # prompt template
    template = ChatPromptTemplate.from_messages(
        [
            ("system", "{instructions}\n\n{context}{news_data}"),
            few_shot_prompt,
            ("human", "JSON Data 1: {realtime_data}\nJSON Data 2: {historical_data}"),
        ]
    )

    return template


def getAIAdvice():
    # prepare things for Bitcoin news
    news, news_instructions, news_template = prepareNews()

    # prepare things for system prompt
    instructions, context, examples = prepareSystemPrompt()

    # prepare data
    realtime_data, historical_data = prepareData()

    # create template
    recommendation_template = createTemplate(examples)

    # desired output format
    json_recommendation_schema = {
        "title": "recommendation",
        "description": "The most complete AI recommendation for trading BTC in the current situation.",
        "type": "object",
        "properties": {
            "decision": {
                "type": "string",
                "description": "Your decision whether to buy, sell or hold BTC.",
            },
            "ratio": {
                "type": "integer",
                "description": """The percentage of assets you decide to buy or sell. 
                           It should be an integer between 0 and 100. If the decision is hold, ratio should be 100.""",
            },
            "reason": {
                "type": "string",
                "description": """Detailed logical reason for your recommendation. 
                            It should be created in consideration of all provided data.""",
            },
        },
        "required": ["decision", "ratio", "reason"],
    }

    # initialize llm object
    try:
        # llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro', google_api_key=GOOGLE_API_KEY)
        llm = ChatVertexAI(model="gemini-1.5-pro")
    except Exception as e:
        print(f"Error in starting a chatting with the LLM model: {e}")

    # new model with structured output
    structured_llm = llm.with_structured_output(json_recommendation_schema)

    def getAdviceArgs(passthrough):
        print(f"Organized News:\n{passthrough.content}")

        advice_arguments = {
            "instructions": instructions,
            "context": context,
            "realtime_data": realtime_data,
            "historical_data": historical_data,
            "news_data": passthrough.content,
        }

        return advice_arguments

    # invoke LLM to get response
    chain = (
        news_template
        | llm
        | RunnableLambda(getAdviceArgs)
        | recommendation_template
        | structured_llm
    )
    try:
        response = chain.invoke(
            {"news_instructions": news_instructions, "news": " ".join(news)}
        )
    except Exception as e:
        print(f"Error in analyzing data with LLM: {e}")
        return None

    # insert recommendation into DB
    DB.insertIntoRecommendation(response)
    return response


def autotrade():
    # get AI advice, there are 3 chances to make well-formatted advice.
    cnt = 0
    while cnt < 3:
        decision = getAIAdvice()
        if decision is not None:
            break
        else:
            cnt += 1
    if cnt == 3:
        return

    # execute the decision
    ratio = decision.get("ratio") / 100
    print(f"AI response:\n{decision}\n")
    if decision.get("decision") == "buy":
        AssetforTest.executeBuy(ratio)  # helper.executeBuy(ratio)
    elif decision.get("decision") == "sell":
        AssetforTest.executeSell(ratio)  # helper.executeSell(ratio)
    else:
        AssetforTest.executeHold()

    return


def main():
    # initialize asset (or load if there exist previous asset info)
    AssetforTest.initializeAsset()

    # initialize DB
    # DB.dropAllTable()
    # DB.createTables()

    # operate trading only once
    autotrade()

    # operate trading every hours
    # schedule.every().hours.do(autotrade)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    return


if __name__ == "__main__":
    main()

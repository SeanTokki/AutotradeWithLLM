import json
import time
import schedule
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
import sqlite3

# import from my codes
from asset import AssetforTest
from helper import *
from DB import *

# API key setup
GOOGLE_API_KEY = "AIzaSyCyONIe9z8p2re0GnOZI3GdBpXl_I9GAXo"
UPBIT_API_KEY = "UPBIT_API_KEY"
YOUTUBE_API_KEY = "AIzaSyAquYzeFa1FXjlplf-54nK572HCDqbiYN0"

# DB setup
CONN = sqlite3.connect('./trading_history.db')
CURSOR = CONN.cursor()

def get_AI_advice(instruction_path, context_path):
    # prepare data
    instructions = read_file(instruction_path)
    context = read_file(context_path)
    examples = [
        {
        "input1": '{"current_time": "2024-04-02 19:50:01", "orderbook": {...}, "btc_balance": 0.1, "krw_balance": 8000000, "btc_avg_price": 80000000}',
        "input2": '{"index": [["daily", "2024-03-07 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
        "output": '{"decision": "hold", "ratio": 100, "reason": "The market is currently experiencing choppy price movements with no clear upward or downward trend. The RSI is hovering around 50, indicating neither overbought nor oversold conditions. Given the uncertainty, it is recommended to hold both the current Bitcoin holding and KRW balance for now. Monitor the market closely for any emerging trends or signals that provide a clearer buying or selling opportunity."}',
        },
        {
        "input1": '{"current_time": "2024-03-20 12:00:00", "orderbook": {...}, "btc_balance": 0.25, "krw_balance": 5000000, "btc_avg_price": 85000000}',
        "input2": '{"index": [["daily", "2024-02-23 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
        "output": '{"decision": "sell", "ratio": 75, "reason": "The market trend suggests a bearish turn with a price decrease over the past 5 minutes. Additionally, the trading volume is low, indicating a potential lack of buying pressure. To minimize potential losses, it is recommended to sell 75% of the current Bitcoin holding at the current market price."}',
        },
        {
        "input1": '{"current_time": "2024-03-25 20:10:07", "orderbook": {...}, "btc_balance": 0.05, "krw_balance": 7500000, "btc_avg_price": 90000000}',
        "input2": '{"index": [["daily", "2024-02-28 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
        "output": '{"decision": "buy", "ratio": 30, "reason": "The market indicates a potential bullish breakout. The price recently touched a support level and surged with a significant increase in volume, suggesting strong buying pressure. It is recommended to buy 30% of the available KRW worth of Bitcoin to capitalize on this potential opportunity."}',
        }
    ]
    real = get_realtime_data()
    historical, btc_price =  get_historical_data()
    realtime_data = json.dumps(real)
    historical_data = json.dumps(historical)

    # save current btc price for test
    AssetforTest.set_btc_price(btc_price)

    # insert asset and price information into DB
    insert_into_asset(CURSOR, CONN, real, btc_price)
    # update the last recommendation's result based on current asset
    update_recommendation_result(CURSOR, CONN)

    # initialize llm object
    try:
        llm = ChatGoogleGenerativeAI(model='gemini-pro', convert_system_message_to_human=True, google_api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Error in starting a chatting with the LLM model: {e}")

    # output formatting
    class Recommendation(BaseModel):
        decision: str = Field(description="Your decision whether to buy, sell or hold.")
        ratio: int = Field(description="The percentage of assets you decide to buy or sell. It should be an integer between 0 and 100. If the decision is hold, ratio should be 100")
        reason: str = Field(description="Detailed logical reason for your recommendation.")
    parser = JsonOutputParser(pydantic_object=Recommendation)

    # few-shot example
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "JSON Data 1: {input1}\nJSON Data 2: {input2}"),
            ("ai", "{output}")
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt = example_prompt,
        examples = examples,
    )

    # final prompt template
    template = ChatPromptTemplate.from_messages(
        [
        ("system", "Instruction: {instructions}\nContext: {context}\nOutput format: {output_format}"),
        few_shot_prompt,
        ("user","JSON Data 1: {realtime_data}\nJSON Data 2: {historical_data}"),
        ]
    )

    # invoke LLM to get response
    chain = template | llm | parser
    try:
        response = chain.invoke({"instructions": instructions, "output_format": parser.get_format_instructions(), "context": context,
                                "realtime_data": realtime_data, "historical_data": historical_data})
    except Exception as e:
        print(f"Error in analyzing data with LLM: {e}")
        return None

    # check if the response is well-formatted
    response = check_format(response)
    if response is not None:
        # insert recommendation into DB
        insert_into_recommendation(CURSOR, CONN, response)
        return response
    else:
        print(f"AI response is not well-formatted. The original response: {response}")
        return None

def make_decision_and_execute(instruction_path, context_path):
    # get AI advice, there are 3 chances to make well-formatted advice.
    cnt = 0
    while cnt < 3:
        decision = get_AI_advice(instruction_path, context_path)
        if decision is not None: 
            break
        else: 
            cnt += 1
    if cnt == 3: 
        return

    # execute the decision
    ratio = decision.get('ratio')
    print(f"AI response: {decision}")
    if decision.get('decision') == "buy":
        AssetforTest.execute_buy(ratio)  # execute_buy(ratio)
    elif decision.get('decision') == "sell":
        AssetforTest.execute_sell(ratio)  # execute_sell(ratio)
    else:
        AssetforTest.execute_hold()

    return

def main():
    instruction_path="./instructions/instructions_240405.md"
    context_path="./instructions/context_240405.md"
    
    # initialize asset
    AssetforTest.initialize_asset()

    # initialize DB
    drop_all_table(CURSOR, CONN)
    create_tables(CURSOR, CONN)

    make_decision_and_execute(instruction_path, context_path)
    # schedule.every(30).minutes.do(make_decision_and_execute, instruction_path, context_path)
    # # operate trading every thirty minutes
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

if __name__ == '__main__':
    main()

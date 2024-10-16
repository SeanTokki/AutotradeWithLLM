from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
import helper

ex_outputs = helper.readJSON("./instructions/examples.json")

examples = [
        {
        "input1": '{"current_time": "2024-04-02 19:50:01", "orderbook": {...}, "btc_balance": 0.1, "krw_balance": 8000000, "btc_avg_price": 80000000}',
        "input2": '{"index": [["daily", "2024-03-07 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
        "output": str(ex_outputs[0])
        },
        {
        "input1": '{"current_time": "2024-03-20 12:00:00", "orderbook": {...}, "btc_balance": 0.25, "krw_balance": 5000000, "btc_avg_price": 85000000}',
        "input2": '{"index": [["daily", "2024-02-23 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
        "output": str(ex_outputs[1])
        },
        {
        "input1": '{"current_time": "2024-03-25 20:10:07", "orderbook": {...}, "btc_balance": 0.05, "krw_balance": 7500000, "btc_avg_price": 90000000}',
        "input2": '{"index": [["daily", "2024-02-28 09:00:00"], ...], "columns": ["open", "high", "low", "close", "volume", ...], "data": [...]}',
        "output": str(ex_outputs[2])
        }
    ]

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

print(few_shot_prompt)
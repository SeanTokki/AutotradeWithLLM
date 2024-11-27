from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal, List, Dict
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from operator import add
import pyupbit
import json

import helper
import tools


# state for graph
class AgentState(TypedDict):
    # for recording
    graph_history: Annotated[List, add]
    recent_message: AIMessage
    # accessible data for manager
    chart_analysis: str
    news_analysis: str
    feedback: str
    # hidden states for staff agent
    chart_data: Annotated[List[Dict[str, Dict[str, Dict[str, float]]]], add]
    news_data: Annotated[List[str], add]
    search_results: Annotated[List[Dict[str, str]], add]
    tool_caller: str
    target_agent: str
    request: str
    # for manager routing
    pending_requests: List[Dict[str, str]]


def portfolioManager(state: AgentState) -> AgentState:
    # read instruction file
    instruction = helper.readFile("./instructions/portfolio_manager_instruction.md")

    # prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{instruction}",
            ),
            (
                "human",
                """
                Currently accessible data is as follows: {accessible_data}

                Please make your best cryptocurrency trading strategy to the trader.
                """,
            ),
        ]
    )

    # new model with tool binding
    llm_tools = [tools.requestAgent]
    # llm = ChatVertexAI(model="gemini-1.5-pro").with_structured_output(Request)
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0).bind_tools(llm_tools)

    # organize current accessible data
    accessible_data = {
        "chart_analysis": state["chart_analysis"],
        "news_analysis": state["news_analysis"],
        "feedback": state["feedback"],
    }

    # invoke llm
    chain = prompt | llm
    response = chain.invoke(
        {"instruction": instruction, "accessible_data": str(accessible_data)}
    )

    # message to record
    message = {"content": response.content, "tool_calls": response.tool_calls}

    if response.tool_calls:
        target_agent = response.tool_calls[0]["args"]["target_agent"]
        content = response.tool_calls[0]["args"]["request"]
    else:
        target_agent = "trader"
        content = response.content

    return {
        "graph_history": [{"agent": "portfolio_manager", "message": message}],
        "recent_message": response,
        "target_agent": target_agent,
        "request": content,
    }


def chartAnalyst(state: AgentState) -> AgentState:
    # read instruction file
    instruction = helper.readFile("./instructions/chart_analyst_instruction.md")

    # prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{instruction} {tickers}",
            ),
            (
                "human",
                """
                Currently accessible chart data is as follows: {chart_data}

                Currently accessible web search results are as follows: {search_results}
                
                {request}
                """,
            ),
        ]
    )

    # new model with tool binding
    llm_tools = [tools.getChartData, tools.webSearch]
    # llm = ChatVertexAI(model="gemini-1.5-pro").bind_tools(llm_tools)
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0).bind_tools(llm_tools)

    # invoke llm
    chain = prompt | llm
    response = chain.invoke(
        {
            "instruction": instruction,
            "tickers": pyupbit.get_tickers("KRW"),
            "chart_data": state["chart_data"],
            "search_results": state["search_results"],
            "request": state["request"],
        }
    )

    # message to record
    message = {"content": response.content, "tool_calls": response.tool_calls}

    return {
        "graph_history": [{"agent": "chart_analyst", "message": message}],
        "recent_message": response,
        "tool_caller": "chart_analyst",
        "chart_analysis": response.content,
    }


def newsAnalyst(state: AgentState) -> AgentState:
    # read instruction file
    instruction = helper.readFile("./instructions/news_analyst_instruction.md")

    # prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{instruction}",
            ),
            (
                "human",
                """
                Currently accessible news data is as follows: {news_data}
                
                Currently accessible web search results are as follows: {search_results}
                
                {request}
                """,
            ),
        ]
    )

    # new model with tool binding
    llm_tools = [tools.getCoinnessNews, tools.webSearch]
    # llm = ChatVertexAI(model="gemini-1.5-pro").bind_tools(llm_tools)
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0).bind_tools(llm_tools)

    # invoke llm
    chain = prompt | llm
    response = chain.invoke(
        {
            "instruction": instruction,
            "news_data": state["news_data"],
            "search_results": state["search_results"],
            "request": state["request"],
        }
    )

    # message to record
    message = {"content": response.content, "tool_calls": response.tool_calls}

    return {
        "graph_history": [{"agent": "news_analyst", "message": message}],
        "recent_message": response,
        "tool_caller": "news_analyst",
        "news_analysis": response.content,
    }


def performanceEvaluator(state: AgentState) -> AgentState:
    response = AIMessage(content="There is no past trading decision to feedback.")

    message = {"content": response.content}

    return {
        "recent_message": response,
        "graph_history": [{"agent": "performance_evaluator", "message": message}],
        "feedback": response.content,
    }

    # read instruction file
    instruction = helper.readFile("./instructions/performance_evaluator_instruction.md")

    # prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{instruction} {tickers}",
            ),
            (
                "human",
                """
                Currently accessible chart data is as follows: {chart_data}
                
                {request}
                """,
            ),
        ]
    )

    # new model with tool binding
    llm_tools = [tools.getChartData]
    # llm = ChatVertexAI(model="gemini-1.5-pro").bind_tools(llm_tools)
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0).bind_tools(llm_tools)

    # invoke llm
    chain = prompt | llm
    response = chain.invoke(
        {
            "instruction": instruction,
            "tickers": pyupbit.get_tickers("KRW"),
            "chart_data": state["chart_data"],
            "request": state["request_content"],
        }
    )

    # message to record
    message = {"content": response.content, "tool_calls": response.tool_calls}

    return {
        "graph_history": [{"agent": "chart_analyst", "message": message}],
        "recent_message": response,
        "tool_caller": "chart_analyst",
        "chart_analysis": response.content,
    }


def trader(state: AgentState) -> AgentState:
    message = {
        "content": f"Final Trading Strategy: {state["request"]}",
        "tool_calls": [],
    }

    return {
        "graph_history": [{"agent": "trader", "message": message}],
    }


def toolExecutor(state: AgentState) -> AgentState:
    available_tools = {
        "getChartData": tools.getChartData,
        "getCoinnessNews": tools.getCoinnessNews,
        "webSearch": tools.webSearch,
    }

    output = {"chart_data": [], "news_data": [], "search_results": []}
    for tool_call in state["recent_message"].tool_calls:
        name, args = tool_call["name"], tool_call["args"]

        try:
            tool_result = available_tools[name].invoke(args)
        except Exception as e:
            print(f"Error while executing a tool: {e}")
            continue

        if name == "getChartData":
            output["chart_data"].append(tool_result)
        elif name == "getCoinnessNews":
            output["news_data"].append(tool_result)
        elif name == "webSearch":
            output["search_results"].append(tool_result)

    return output


# Routing function for staffs
def staffRouter(state: AgentState) -> str:
    if state["recent_message"].tool_calls:
        return "tool_executor"
    else:
        return "portfolio_manager"


# Routing function for portfolio manager
def managerRouter(state: AgentState) -> str:
    return state["target_agent"]


# Routing function for tool executor
def toolRouter(state: AgentState) -> str:
    return state["tool_caller"]


load_dotenv()

# initialize state graph
graph = StateGraph(AgentState)

# initialize tool node
tool_node = ToolNode([tools.getChartData, tools.getCoinnessNews])

# add nodes to graph
graph.add_node("portfolio_manager", portfolioManager)
graph.add_node("chart_analyst", chartAnalyst)
graph.add_node("news_analyst", newsAnalyst)
graph.add_node("performance_evaluator", performanceEvaluator)
graph.add_node("trader", trader)
graph.add_node("tool_executor", toolExecutor)

# add edges to graph
graph.add_edge(START, "portfolio_manager")
graph.add_conditional_edges(
    "portfolio_manager",
    managerRouter,
    {
        "chart_analyst": "chart_analyst",
        "news_analyst": "news_analyst",
        "performance_evaluator": "performance_evaluator",
        "trader": "trader",
    },
)
graph.add_conditional_edges(
    "chart_analyst",
    staffRouter,
    {"tool_executor": "tool_executor", "portfolio_manager": "portfolio_manager"},
)
graph.add_conditional_edges(
    "news_analyst",
    staffRouter,
    {"tool_executor": "tool_executor", "portfolio_manager": "portfolio_manager"},
)
graph.add_conditional_edges(
    "performance_evaluator",
    staffRouter,
    {"tool_executor": "tool_executor", "portfolio_manager": "portfolio_manager"},
)
graph.add_conditional_edges(
    "tool_executor",
    toolRouter,
    {
        "chart_analyst": "chart_analyst",
        "news_analyst": "news_analyst",
        "performance_evaluator": "performance_evaluator",
    },
)
graph.add_edge("trader", END)

app = graph.compile()

# from IPython.display import Image, display

# try:
#     display(Image(app.get_graph(xray=True).draw_mermaid_png()))
# except Exception as e:
#     print(f"{e}")

config = RunnableConfig(recursion_limit=20, configurable={"thread_id": "AUTOTRADE"})
result = app.invoke(
    input={
        "chart_data": [],
        "news_data": [],
        "search_results": [],
        "chart_analysis": "",
        "news_analysis": "",
        "feedback": "",
        "graph_history": [],
        "recent_message": AIMessage(content=""),
        "tool_caller": "",
        "target_agent": "",
        "request": "",
    },
    config=config,
)

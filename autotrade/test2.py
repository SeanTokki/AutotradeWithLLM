import helper
import autotrade
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

GOOGLE_API_KEY = "AIzaSyCyONIe9z8p2re0GnOZI3GdBpXl_I9GAXo"

# prepare things for Bitcoin news
news, news_instructions, news_template = autotrade.prepareNews()

# prepare things for system prompt
instructions, context, examples = autotrade.prepareSystemPrompt()

# prepare chart and asset data
realtime_data, historical_data = autotrade.prepareData()

# create output parser
parser = autotrade.createOutputParser()

# create template
template = autotrade.createTemplate(examples)

# initialize llm object
try:
    llm = ChatGoogleGenerativeAI(model='gemini-pro', convert_system_message_to_human=True, google_api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Error in starting a chatting with the LLM model: {e}")

# set functions to get arguments
def getNewsArgs(_):
    news_arguments = {
    "news_instructions": news_instructions,
    "news": news
    }

    return news_arguments

def getAdviceArgs(passthrough):
    print(f"Organized News: {passthrough.content}")
    
    advice_arguments = {
    "instructions": instructions, 
    "output_format": parser.get_format_instructions(), 
    "context": context,
    "realtime_data": realtime_data, 
    "historical_data": historical_data,
    "news_data": passthrough.content
    }

    return advice_arguments

# invoke LLM to get response
chain = news_template | llm | RunnableLambda(getAdviceArgs) | template | llm | parser

try:
    response = chain.invoke({"news_instructions": news_instructions, "news": news})
    print(response)
except Exception as e:
    print(f"Error in analyzing data with LLM: {e}")
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field

load_dotenv()

class TradingRecommendation(BaseModel):
    action: str = Field(description="Buy, Sell, or Hold")
    reason: str = Field(description="Professional explanation based on technical indicators")

llm = GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

parser = JsonOutputParser(pydantic_object=TradingRecommendation)
parser2 = StrOutputParser()

prompt = PromptTemplate(
    template="""
You are a world-class crypto trading strategist with deep expertise in technical analysis, quantitative modeling, and market psychology.

Given real-time technical indicators for a cryptocurrency, determine the best action: **Buy**, **Sell**, or **Hold**.

---

### Technical Indicators:
- Current Price: {current_price}
- Price Change in Last Hour (%): {price_change_1h}
- Market Cap Rank: {market_cap_rank}
- 24h Trading Volume (USD): {total_volume}
- RSI: {rsi}
- MACD Histogram: {macd_histogram}
- balanceUSD : {balanceUSD}

---

### Output Format (strict JSON):
{format_instructions}

Respond concisely (1–2 lines reasoning).
""",
    input_variables=["price", "change_1h", "market_cap_rank", "total_volume", "rsi", "macd_histogram"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

prompt2 = PromptTemplate(
    input_variables=["coin_name"],
    template=(
        "You are a crypto expert.\n"
        "Given a coin name like 'ethereum', return its coin id (e.g., 'eth').\n"
        "Respond with only the id\."
    )
)

chain = prompt | llm | parser
chain2 = prompt2 | llm | parser2

def get_llm_action(features: dict) -> dict:
    try:
        return chain.invoke(features)
    except Exception as e:
        print("LLM Error:", e)
        return {"action": "Hold", "reason": str(e)}

def get_id(coin_name: str) -> str:
    try:
        return chain2.invoke({"coin_name": coin_name})
    except Exception as e:
        print("LLM Error:", e)
        return coin_name.lower()

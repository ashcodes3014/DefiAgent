from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class TradingRecommendation(BaseModel):
    action: str = Field(description="Buy, Sell, or Hold")
    reason: str = Field(description="Professional explanation based on technical indicators")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
parser = JsonOutputParser(pydantic_object=TradingRecommendation)
parser2 = StrOutputParser()

prompt = PromptTemplate(
    template="""
You are a world-class crypto trading strategist with deep expertise in technical analysis, quantitative modeling, and market psychology.

Given real-time technical indicators for a cryptocurrency, perform **professional-level reasoning** to determine the best action: **Buy**, **Sell**, or **Hold**.

Apply:
- Cross-signal validation: correlate RSI, MACD, volume, and price movement
- Threshold logic: e.g., RSI > 70 (overbought), MACD < 0 (bearish momentum)
- Volume-price analysis: detect fakeouts vs real trends
- Market sentiment estimation
- Momentum & volatility from MACD histogram and hourly change

---

### Technical Indicators:
- Current Price: {current_price}
- Price Change in Last Hour (%): {price_change_1h}
- Market Cap Rank: {market_cap_rank}
- 24h Trading Volume (USD): {total_volume}
- RSI: {rsi}
- MACD Histogram: {macd_histogram}

---

### Output Format (strict JSON):
{format_instructions}

Your reasoning must be **professional but concise (1–2 lines max)** — like a note you'd send to a busy trader.
""",
    input_variables=[
        "price", "change_1h", "market_cap_rank", "total_volume", "rsi", "macd_histogram"
    ],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

prompt2 = PromptTemplate(
    input_variables=["coin_id"],
    template=(
        "You are a crypto expert.\n"
        "Given a coin ID like 'eth', return its full coin name (e.g., 'ethereum').\n"
        "Respond with only the name, no explanation.\n"
        "Coin ID: {coin_id}"
    )
)

chain = prompt | llm | parser
chain2 = prompt2 | llm | parser2

def get_llm_action(features: dict) -> dict:
    try:
        output = chain.invoke(features)
        return output
    except Exception as e:
        print("LLM Error:", e)
        return {"error": str(e)}

def get_name(coin_id: str) -> str:
    try:
        output = chain2.invoke({"coin_id": coin_id})
        return output
    except Exception as e:
        print("LLM Error:", e)
        return {"error": str(e)}

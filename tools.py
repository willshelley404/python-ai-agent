# tools.py

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import re
import yfinance as yf
import os
from fredapi import Fred

print("FRED KEY:", os.getenv("FRED_API_KEY"))
# ----------------------------
# Input Schemas
# ----------------------------
class SearchInput(BaseModel):
    query: str = Field(description="Search query")

class FinancialInput(BaseModel):
    query: str = Field(description="Financial query like stock price, CPI, GDP, WTI")

# ----------------------------
# Search Tool
# ----------------------------
search = DuckDuckGoSearchRun()

search_tool = StructuredTool.from_function(
    func=search.run,
    name="search",
    description="Search the web for general information",
    args_schema=SearchInput
)

# ----------------------------
# Financial Tool Function
# ----------------------------
def financial_func(query: str):
    query_lower = query.lower()

    # ----------------------------
    # FRED setup
    # ----------------------------
    fred = None
    if os.getenv("FRED_API_KEY"):
        fred = Fred(api_key=os.getenv("FRED_API_KEY"))

    # ----------------------------
    # CPI
    # ----------------------------
    if "cpi" in query_lower or "inflation" in query_lower:
        if fred:
            try:
                data = fred.get_series("CPIAUCSL")
                value = data.iloc[-1]
                date = data.index[-1].strftime("%Y-%m")
                return f"CPI is {value:.2f} as of {date}"
            except Exception as e:
                return f"Error fetching CPI: {str(e)}"
        return "FRED API key not configured"

    # ----------------------------
    # Unemployment
    # ----------------------------
    if "unemployment" in query_lower:
        if fred:
            try:
                data = fred.get_series("UNRATE")
                value = data.iloc[-1]
                date = data.index[-1].strftime("%Y-%m")
                return f"Unemployment rate is {value:.1f}% as of {date}"
            except Exception as e:
                return f"Error fetching unemployment: {str(e)}"
        else:
            return "FRED API key not configured"

    # ----------------------------
    # GDP
    # ----------------------------
    if "gdp" in query_lower:
        if fred:
            try:
                data = fred.get_series("GDP")
                value = data.iloc[-1]
                date = data.index[-1].strftime("%Y-%m")
                return f"GDP is {value:,.0f} (millions USD) as of {date}"
            except Exception as e:
                return f"Error fetching GDP: {str(e)}"

    # ----------------------------
    # Stock ticker
    # ----------------------------
    ticker_match = re.findall(r"\b[A-Z]{1,5}\b", query)
    if ticker_match:
        ticker_symbol = ticker_match[-1]

        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1d")

            if hist.empty:
                return f"No price data found for {ticker_symbol}"

            price = hist["Close"].iloc[-1]
            return f"{ticker_symbol} is trading at ${price:.2f}"

        except Exception as e:
            return f"Error fetching {ticker_symbol}: {str(e)}"

    # ----------------------------
    # WTI crude oil
    # ----------------------------
    if "wti" in query_lower or "crude oil" in query_lower:
        try:
            wti = yf.Ticker("CL=F")
            hist = wti.history(period="1d")

            if hist.empty:
                return "No WTI price data available"

            price = hist["Close"].iloc[-1]
            return f"WTI crude oil is ${price:.2f} per barrel"

        except Exception as e:
            return f"Error fetching WTI: {str(e)}"

    return "No financial data found"

# ----------------------------
# Financial Tool
# ----------------------------
financial_tool = StructuredTool.from_function(
    func=financial_func,
    name="financial_tool",
    description="Fetch stock prices, commodities, and economic indicators like CPI, GDP, unemployment",
    args_schema=FinancialInput
)
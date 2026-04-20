# Research Agent (LangChain + Groq)

Lightweight research agent using LangChain, Groq (LLaMA 3.3), and custom tools for web search and financial data. Outputs are strictly structured via Pydantic.

## Features

- Tool-based reasoning:
  - `search` for general queries
  - `financial_tool` for stocks, CPI, GDP, unemployment, WTI
- Structured JSON output enforced with Pydantic
- Real data via FRED API and Yahoo Finance
- Simple CLI interface

## Project Structure


.
├── research_agent_modern.py
├── tools.py
├── .env
└── README.md


## Setup

Install dependencies:

```bash
pip install langchain langchain-core langchain-community langchain-groq \
            pydantic python-dotenv yfinance fredapi duckduckgo-search

```
## Create `.env`:

GROQ_API_KEY=your_key
FRED_API_KEY=your_key  # optional

## Usage


`python research_agent_modern.py`

## Output Schema

``` JSON
{
  "topic": "string",
  "summary": "string",
  "sources": ["string"],
  "tools_used": ["string"]
}
```

## Tools
- `search`: DuckDuckGo web search
- `financial_tool`:
    - Stocks via yfinance
    - CPI, GDP, unemployment via FRED
    - crude via yfinance


## Notes

Python 3.13 fix:

``` python
import builtins, uuid
builtins.uuid = uuid
```

- Ticker detection uses regex and may produce false positives
- FRED API required for macroeconomic data
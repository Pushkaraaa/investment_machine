"""
Finology Ticker API implementation for stock screening.
This module uses Finology's API to screen and fetch stock details.
"""
import requests
import logging
from typing import Dict, List, Any, Optional

from .base_screener import BaseScreener

logger = logging.getLogger(__name__)

class FinologyScreener(BaseScreener):
    """
    Concrete screener that uses Finology's public API to screen and fetch stock details.
    """
    def __init__(self, api_key: str, base_url: str = "https://api.finology.in"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal helper to send GET requests with authentication and basic error handling.
        """
        try:
            url = f"{self.base_url}{path}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {}
        except ValueError as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            return {}

    def get_available_criteria(self) -> Dict[str, Any]:
        """
        Fetch or define the set of supported screening filters (e.g. sectors, market cap ranges).
        """
        # Option A: call a Finology metadata endpoint
        # return self._get("/v1/screener/criteria")  
        
        # Option B: hard‐code allowed values
        return {
            "sector": ["Technology", "Financials", "Healthcare", "Consumer Goods", "Industrials", 
                      "Utilities", "Materials", "Energy", "Communication Services", "Real Estate"],
            "marketCapMin": {
                "type": "number",
                "description": "Minimum market capitalization in INR",
                "examples": [1_000_000_000, 10_000_000_000, 100_000_000_000]
            },
            "marketCapMax": {
                "type": "number",
                "description": "Maximum market capitalization in INR",
                "examples": [10_000_000_000, 100_000_000_000, 1_000_000_000_000]
            },
            "exchange": ["NSE", "BSE"],
            "peRatioMin": {
                "type": "number",
                "description": "Minimum P/E ratio",
                "examples": [0, 5, 10]
            },
            "peRatioMax": {
                "type": "number",
                "description": "Maximum P/E ratio",
                "examples": [15, 20, 30, 50]
            },
            "dividendYieldMin": {
                "type": "number",
                "description": "Minimum dividend yield percentage",
                "examples": [1, 2, 3, 5]
            },
            "roeMin": {
                "type": "number",
                "description": "Minimum Return on Equity percentage",
                "examples": [10, 15, 20]
            },
            "debtToEquityMax": {
                "type": "number",
                "description": "Maximum Debt to Equity ratio",
                "examples": [0.5, 1, 2]
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of results to return",
                "default": 100,
                "examples": [10, 25, 50, 100]
            },
            "page": {
                "type": "number",
                "description": "Page number for pagination",
                "default": 1,
                "examples": [1, 2, 3]
            }
        }

    def screen(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use Finology's screener endpoint to fetch stocks matching the given criteria.
        """
        try:
            # Convert your generic dict into the API's expected params
            params = {
                "sector": criteria.get("sector"),
                "market_cap_min": criteria.get("marketCapMin"),
                "market_cap_max": criteria.get("marketCapMax"),
                "exchange": criteria.get("exchange"),
                "pe_ratio_min": criteria.get("peRatioMin"),
                "pe_ratio_max": criteria.get("peRatioMax"),
                "dividend_yield_min": criteria.get("dividendYieldMin"),
                "roe_min": criteria.get("roeMin"),
                "debt_to_equity_max": criteria.get("debtToEquityMax"),
                "limit": criteria.get("limit", 100),
                "page": criteria.get("page", 1)
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            data = self._get("/v1/screener/search", params=params)
            
            # Suppose the API returns { "results": [ {ticker, name, price, ...}, ... ] }
            results = data.get("results", [])
            
            # Normalize field names to a standard format
            normalized_results = []
            for stock in results:
                normalized_results.append({
                    "ticker": stock.get("symbol"),
                    "name": stock.get("companyName"),
                    "price": stock.get("latestPrice"),
                    "marketCap": stock.get("marketCap"),
                    "sector": stock.get("sector"),
                    "peRatio": stock.get("peRatio"),
                    "dividendYield": stock.get("dividendYield"),
                    "roe": stock.get("roe"),
                    "debtToEquity": stock.get("debtToEquity")
                })
            
            return normalized_results
        except Exception as e:
            logger.error(f"Error during screening: {str(e)}")
            return []

    def get_stock_details(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a single ticker.
        """
        try:
            data = self._get(f"/v1/stocks/{ticker}")
            if not data:
                logger.error(f"Failed to fetch details for ticker: {ticker}")
                return {}
            
            # Normalize or pick only the fields you care about
            details = {
                "ticker": data.get("symbol"),
                "name": data.get("companyName"),
                "sector": data.get("sector"),
                "industry": data.get("industry"),
                "price": data.get("latestPrice"),
                "change": data.get("change"),
                "changePercent": data.get("changePercent"),
                "open": data.get("open"),
                "high": data.get("high"),
                "low": data.get("low"),
                "volume": data.get("volume"),
                "marketCap": data.get("marketCap"),
                "peRatio": data.get("peRatio"),
                "dividendYield": data.get("dividendYield"),
                "roe": data.get("roe"),
                "roa": data.get("roa"),
                "debtToEquity": data.get("debtToEquity"),
                "currentRatio": data.get("currentRatio"),
                "eps": data.get("ttmEPS"),
                "beta": data.get("beta"),
                "fiftyTwoWeekHigh": data.get("week52High"),
                "fiftyTwoWeekLow": data.get("week52Low"),
                "ytdChangePercent": data.get("ytdChangePercent"),
                "financials": data.get("financials", {}),
                "balanceSheet": data.get("balanceSheet", {}),
                "cashFlow": data.get("cashFlow", {})
            }
            
            # Remove None values
            details = {k: v for k, v in details.items() if v is not None}
            
            return details
        except Exception as e:
            logger.error(f"Error fetching stock details for {ticker}: {str(e)}")
            return {} 
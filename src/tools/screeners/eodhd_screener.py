"""
EODHD API implementation for stock screening.
This module uses EODHD's Financial Data APIs to screen and fetch stock details.
"""
import os
import requests
import logging
from typing import Dict, List, Any, Optional

from .base_screener import BaseScreener

logger = logging.getLogger(__name__)

class EODHDScreener(BaseScreener):
    """
    Concrete BaseScreener using EODHD's Financial Data APIs.
    Quick-start docs: https://eodhd.com/financial-apis/quick-start-with-our-financial-data-apis
    """

    def __init__(self, api_token: str = None):
        """
        Initialize EODHD screener.
        
        Args:
            api_token: API token for EODHD. If not provided, will look for EODHD_API_TOKEN env var.
        """
        self.api_token = api_token or os.getenv("EODHD_API_TOKEN")
        if not self.api_token:
            raise ValueError("Set EODHD_API_TOKEN env var or pass api_token")
        self.base = "https://eodhd.com/api/"
    
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Internal helper to send GET requests to EODHD API.
        
        Args:
            path: API endpoint path
            params: Additional query parameters
            
        Returns:
            JSON response from the API
        """
        try:
            url = f"{self.base}{path}"
            p = {"api_token": self.api_token, "fmt": "json"}
            if params:
                p.update(params)
            resp = requests.get(url, params=p, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"EODHD API request failed: {str(e)}")
            return {}
        except ValueError as e:
            logger.error(f"Failed to parse EODHD API response: {str(e)}")
            return {}

    def get_available_criteria(self) -> Dict[str, Any]:
        """
        Get available screening criteria for EODHD.
        
        Returns:
            Dictionary of available criteria and their descriptions
        """
        return {
            "exchange": {
                "type": "string",
                "description": "Stock exchange to screen",
                "options": ["NSE", "BSE", "US"],
                "default": "NSE"
            },
            "market_cap_min": {
                "type": "number",
                "description": "Minimum market capitalization in local currency",
                "default": 1e8,
                "examples": [1e8, 1e9, 1e10]
            },
            "market_cap_max": {
                "type": "number",
                "description": "Maximum market capitalization in local currency",
                "default": 1e12,
                "examples": [1e10, 1e11, 1e12]
            },
            "pe_ratio_min": {
                "type": "number",
                "description": "Minimum P/E ratio",
                "default": 0.0,
                "examples": [0, 5, 10]
            },
            "pe_ratio_max": {
                "type": "number",
                "description": "Maximum P/E ratio",
                "default": 100.0,
                "examples": [20, 50, 100]
            },
            "div_yield_min": {
                "type": "number",
                "description": "Minimum dividend yield (as decimal, not percentage)",
                "default": 0.0,
                "examples": [0.0, 0.01, 0.02]
            },
            "div_yield_max": {
                "type": "number",
                "description": "Maximum dividend yield (as decimal, not percentage)",
                "default": 0.1,
                "examples": [0.05, 0.07, 0.1]
            },
            "price_min": {
                "type": "number",
                "description": "Minimum stock price",
                "default": 1.0,
                "examples": [1, 10, 50]
            },
            "price_max": {
                "type": "number",
                "description": "Maximum stock price",
                "default": 1e4,
                "examples": [100, 1000, 10000]
            },
            "limit": {
                "type": "number",
                "description": "Maximum number of results to return",
                "default": 100,
                "examples": [10, 20, 50, 100]
            }
        }

    def screen(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Screen stocks based on given criteria using EODHD API.
        
        Args:
            criteria: Dictionary with screening parameters
            
        Returns:
            List of dictionaries containing stock information that matches the criteria
        """
        try:
            # Set default values for missing criteria
            defaults = {
                "exchange": "NSE",
                "market_cap_min": 1e8,
                "market_cap_max": 1e12,
                "pe_ratio_min": 0.0,
                "pe_ratio_max": 100.0,
                "div_yield_min": 0.0,
                "div_yield_max": 0.1,
                "price_min": 1.0,
                "price_max": 1e4,
                "limit": 100
            }
            
            # Apply defaults for missing criteria
            for key, default_value in defaults.items():
                if key not in criteria:
                    criteria[key] = default_value
            
            exch = criteria.get("exchange", "NSE")
            logger.info(f"Fetching symbols for exchange: {exch}")
            
            # 1. List symbols on the exchange
            symbols = self._get(f"exchange-symbol-list/{exch}", {})  
            if not symbols:
                logger.error(f"Failed to get symbols for exchange: {exch}")
                return []
                
            logger.info(f"Found {len(symbols)} symbols on {exch}, applying filters...")
            
            results = []
            limit = criteria.get("limit", 100)
            processed = 0
            
            for sym in symbols:
                processed += 1
                if len(results) >= limit:
                    break
                    
                # Progress logging
                if processed % 10 == 0:
                    logger.info(f"Processed {processed}/{len(symbols)} symbols, found {len(results)} matches...")
                
                code = sym.get("Code")
                if not code:
                    continue
                    
                try:
                    # 2. Fetch fundamentals for the symbol
                    data = self._get(f"fundamentals/{code}")
                    gen = data.get("General", {})
                    hist = data.get("EOD", [])
                    latest = hist[-1] if hist else {}
                    
                    # 3. Extract fields
                    mc = float(gen.get("MarketCapitalization") or 0)
                    pe = float(gen.get("PERatio") or 0)
                    dy = float(gen.get("DividendYield") or 0)
                    price = float(latest.get("close") or 0)
                    
                    # 4. Apply filters
                    if not (criteria["market_cap_min"] <= mc <= criteria["market_cap_max"]):
                        continue
                    if not (criteria["pe_ratio_min"] <= pe <= criteria["pe_ratio_max"]):
                        continue
                    if not (criteria["div_yield_min"] <= dy <= criteria["div_yield_max"]):
                        continue
                    if not (criteria["price_min"] <= price <= criteria["price_max"]):
                        continue
                    
                    # 5. Add to results
                    results.append({
                        "ticker": code,
                        "name": gen.get("Name"),
                        "sector": gen.get("Sector"),
                        "industry": gen.get("Industry"),
                        "marketCap": mc,
                        "peRatio": pe,
                        "dividendYield": dy,
                        "price": price,
                        "exchange": exch
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing symbol {code}: {str(e)}")
                    continue
            
            logger.info(f"Screening complete. Found {len(results)} matching stocks.")
            return results
            
        except Exception as e:
            logger.error(f"Error during screening: {str(e)}")
            return []

    def get_stock_details(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific stock from EODHD.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing detailed stock information
        """
        try:
            logger.info(f"Fetching details for {ticker}")
            data = self._get(f"fundamentals/{ticker}")
            
            if not data:
                logger.error(f"Failed to fetch details for ticker: {ticker}")
                return {}
                
            gen = data.get("General", {})
            hist = data.get("EOD", [])
            latest = hist[-1] if hist else {}
            
            # Get financial statements if available
            financials = {
                "IncomeStatement": data.get("Income_Statement", {}),
                "BalanceSheet": data.get("Balance_Sheet", {}),
                "CashFlow": data.get("Cash_Flow", {})
            }
            
            # Build and return a comprehensive details object
            details = {
                "ticker": gen.get("Symbol"),
                "name": gen.get("Name"),
                "description": gen.get("Description"),
                "sector": gen.get("Sector"),
                "industry": gen.get("Industry"),
                "country": gen.get("Country"),
                "exchange": gen.get("Exchange"),
                "currency": gen.get("Currency"),
                "marketCap": gen.get("MarketCapitalization"),
                "peRatio": gen.get("PERatio"),
                "pbRatio": gen.get("PBRatio"),
                "dividendYield": gen.get("DividendYield"),
                "dividendShare": gen.get("DividendShare"),
                "eps": gen.get("EPS"),
                "roe": gen.get("ROE"),
                "roa": gen.get("ROA"),
                "debtToEquity": gen.get("DebtToEquity"),
                "currentRatio": gen.get("CurrentRatio"),
                "beta": gen.get("Beta"),
                "fiftyTwoWeekHigh": gen.get("52WeekHigh"),
                "fiftyTwoWeekLow": gen.get("52WeekLow"),
                "latestPrice": latest.get("close"),
                "volume": latest.get("volume"),
                "change": latest.get("adjusted_close", latest.get("close", 0)) - latest.get("open", 0) if latest else None,
                "changePercent": ((latest.get("adjusted_close", latest.get("close", 0)) / latest.get("open", 1)) - 1) * 100 if latest and latest.get("open") else None,
                "financials": financials
            }
            
            # Remove None values
            details = {k: v for k, v in details.items() if v is not None}
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting stock details for {ticker}: {str(e)}")
            return {} 
import os
import requests
from typing import Dict, Any, Optional
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AlphaVantageClient:
    """Client for interacting with the Alpha Vantage API."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Alpha Vantage client.
        
        Args:
            api_key: Alpha Vantage API key. If not provided, will look for 
                    ALPHA_VANTAGE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key must be provided "
                "or set as ALPHA_VANTAGE_API_KEY environment variable"
            )
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make a request to the Alpha Vantage API.
        
        Args:
            params: Query parameters for the request
            
        Returns:
            API response as a dictionary
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: On API-side errors
        """
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Request to Alpha Vantage failed: {e}")
            raise
        
        if "Error Message" in data:
            logger.error(f"Alpha Vantage API error: {data['Error Message']}")
            raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
        
        if "Note" in data:
            logger.warning(f"Alpha Vantage API note: {data['Note']}")
        
        return data

    def get_daily_adjusted(self, symbol: str, outputsize: str = "compact") -> pd.DataFrame:
        """
        Get daily adjusted time series for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "IBM")
            outputsize: "compact" for last 100 data points, "full" for full history
            
        Returns:
            DataFrame with daily adjusted OHLCV data
        """
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize
        }
        
        data = self._make_request(params)
        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            return pd.DataFrame()
            
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        # Rename columns from "1. open" → "open", etc.
        df.columns = [col.split(". ")[1] for col in df.columns]
        # Convert all columns to numeric
        df = df.apply(pd.to_numeric)
        return df
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        params = {"function": "OVERVIEW", "symbol": symbol}
        return self._make_request(params)

    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        params = {"function": "INCOME_STATEMENT", "symbol": symbol}
        return self._make_request(params)
    
    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        params = {"function": "BALANCE_SHEET", "symbol": symbol}
        return self._make_request(params)
    
    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        params = {"function": "CASH_FLOW", "symbol": symbol}
        return self._make_request(params)
    
    def get_news_sentiment(
        self,
        symbol: Optional[str] = None,
        topics: Optional[str] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        params: Dict[str, str] = {"function": "NEWS_SENTIMENT", "limit": str(limit)}
        if symbol:
            params["tickers"] = symbol
        if topics:
            params["topics"] = topics
        if time_from:
            params["time_from"] = time_from
        if time_to:
            params["time_to"] = time_to
        return self._make_request(params)
    
    def calculate_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate P/E, P/B, dividend yield, margins, ROE, ROA, and debt/equity.
        """
        try:
            ov = self.get_company_overview(symbol)
            inc = self.get_income_statement(symbol)
            bal = self.get_balance_sheet(symbol)
            
            metrics = {
                "Price": float(ov.get("Price", 0)),
                "MarketCap": float(ov.get("MarketCapitalization", 0)),
                "PE_Ratio": float(ov.get("PERatio", 0)),
                "PB_Ratio": float(ov.get("PriceToBookRatio", 0)),
                "DividendYield": float(ov.get("DividendYield", 0)) * 100
            }
            
            if inc.get("annualReports") and bal.get("annualReports"):
                latest_inc = inc["annualReports"][0]
                latest_bal = bal["annualReports"][0]
                
                rev = float(latest_inc.get("totalRevenue", 0))
                net = float(latest_inc.get("netIncome", 0))
                assets = float(latest_bal.get("totalAssets", 0))
                equity = float(latest_bal.get("totalShareholderEquity", 0))
                debt = float(latest_bal.get("shortLongTermDebtTotal", 0))
                
                metrics.update({
                    "NetProfitMargin": (net / rev * 100) if rev else 0,
                    "ROE": (net / equity * 100) if equity else 0,
                    "ROA": (net / assets * 100) if assets else 0,
                    "DebtToEquity": (debt / equity) if equity else 0
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating metrics for {symbol}: {e}")
            return {"error": str(e)}


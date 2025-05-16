import os
import requests
from typing import Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AlphaVantageClient:
    """Client for interacting with the Alpha Vantage API."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Alpha Vantage client.
        
        Args:
            api_key: Alpha Vantage API key. If not provided, looks for
                     ALPHA_VANTAGE_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key must be provided or set as ALPHA_VANTAGE_API_KEY environment variable"
            )
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make a GET request to the Alpha Vantage API.
        
        Args:
            params: Query parameters for the request.
        Returns:
            Parsed JSON response.
        Raises:
            ValueError on API errors, requests.RequestException on network issues.
        """
        params["apikey"] = self.api_key
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        
        if "Error Message" in data:
            msg = data["Error Message"]
            logger.error(f"Alpha Vantage API error: {msg}")
            raise ValueError(f"Alpha Vantage API error: {msg}")
        
        if "Note" in data:
            note = data["Note"]
            logger.warning(f"Alpha Vantage API note: {note}")
        
        return data
    
    def get_daily_adjusted(self, symbol: str, outputsize: str = "compact") -> pd.DataFrame:
        """
        Get daily adjusted time series for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL" or "MSFT").
            outputsize: "compact" (last 100 points) or "full" (full history).
        Returns:
            DataFrame indexed by date with columns: open, high, low, close, adjusted_close, volume, dividend_amount, split_coefficient.
        """
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize
        }
        data = self._make_request(params)
        series = data.get("Time Series (Daily)", {})
        if not series:
            return pd.DataFrame()
        
        df = pd.DataFrame.from_dict(series, orient="index")
        df.index = pd.to_datetime(df.index)
        df.columns = [
            "open", "high", "low", "close", "adjusted_close",
            "volume", "dividend_amount", "split_coefficient"
        ]
        return df.apply(pd.to_numeric)
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview for a symbol.
        
        Args:
            symbol: Stock symbol.
        Returns:
            Dictionary with company fundamentals (e.g., MarketCapitalization, PERatio).
        """
        params = {"function": "OVERVIEW", "symbol": symbol}
        return self._make_request(params)
    
    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Get annual and quarterly income statements."""
        params = {"function": "INCOME_STATEMENT", "symbol": symbol}
        return self._make_request(params)
    
    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """Get annual and quarterly balance sheets."""
        params = {"function": "BALANCE_SHEET", "symbol": symbol}
        return self._make_request(params)
    
    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """Get annual and quarterly cash flow statements."""
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
        """
        Get news and sentiment data.
        """
        params: Dict[str, str] = {
            "function": "NEWS_SENTIMENT",
            "limit": str(limit)
        }
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
        Calculate key financial metrics: P/E, P/B, dividend yield, margins, ROE, ROA, debt/equity.
        """
        try:
            ov = self.get_company_overview(symbol)
            inc = self.get_income_statement(symbol)
            bal = self.get_balance_sheet(symbol)
            
            metrics: Dict[str, Any] = {
                "Price": float(ov.get("Price", 0)),
                "MarketCap": float(ov.get("MarketCapitalization", 0)),
                "PE_Ratio": float(ov.get("PERatio", 0)),
                "PB_Ratio": float(ov.get("PriceToBookRatio", 0)),
                "DividendYield": float(ov.get("DividendYield", 0)) * 100
            }
            
            if inc.get("annualReports") and bal.get("annualReports"):
                li = inc["annualReports"][0]
                lb = bal["annualReports"][0]
                
                rev = float(li.get("totalRevenue", 0))
                net = float(li.get("netIncome", 0))
                assets = float(lb.get("totalAssets", 0))
                equity = float(lb.get("totalShareholderEquity", 0))
                debt = float(lb.get("shortLongTermDebtTotal", 0))
                
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

# Example usage:
if __name__ == "__main__":
    client = AlphaVantageClient(api_key="YOUR_API_KEY")
    
    # Fetch and print company overview
    overview = client.get_company_overview("AAPL")
    print("Overview:", overview)
    
    # Fetch and preview daily adjusted data
    df = client.get_daily_adjusted("AAPL", outputsize="compact")
    print(df.head())
    
    # Calculate key metrics
    metrics = client.calculate_key_metrics("AAPL")
    print("Key Metrics:", metrics)

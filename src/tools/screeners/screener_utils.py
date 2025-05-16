"""
Utility class for working with multiple screeners and performing common screening operations.
"""
import logging
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_screener import BaseScreener

logger = logging.getLogger(__name__)

class ScreenerUtils:
    """
    Utility class for stock screening operations.
    Provides methods for working with multiple screeners and common screening tasks.
    """
    
    def __init__(self, screeners: Dict[str, BaseScreener] = None):
        """
        Initialize with a dictionary of screeners.
        
        Args:
            screeners: Dictionary mapping screener names to screener instances
        """
        self.screeners = screeners or {}
    
    def add_screener(self, name: str, screener: BaseScreener) -> None:
        """
        Add a screener to the utility.
        
        Args:
            name: Name to identify the screener
            screener: Screener instance
        """
        self.screeners[name] = screener
    
    def screen_with_provider(self, provider: str, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Screen stocks using a specific provider.
        
        Args:
            provider: Name of the screener provider to use
            criteria: Screening criteria
            
        Returns:
            List of stocks matching the criteria
        """
        if provider not in self.screeners:
            logger.error(f"Screener provider '{provider}' not found.")
            return []
        
        return self.screeners[provider].screen(criteria)
    
    def screen_parallel(self, criteria: Dict[str, Any], providers: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Screen stocks using multiple providers in parallel.
        
        Args:
            criteria: Screening criteria
            providers: List of provider names to use (uses all providers if None)
            
        Returns:
            Dictionary mapping provider names to their screening results
        """
        providers = providers or list(self.screeners.keys())
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(len(providers), 5)) as executor:
            future_to_provider = {
                executor.submit(self.screen_with_provider, provider, criteria): provider
                for provider in providers if provider in self.screeners
            }
            
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    results[provider] = future.result()
                except Exception as e:
                    logger.error(f"Error screening with {provider}: {str(e)}")
                    results[provider] = []
        
        return results
    
    def combine_results(self, results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Combine results from multiple providers into a single list.
        Merges information about the same ticker from different providers.
        
        Args:
            results: Dictionary mapping provider names to screening results
            
        Returns:
            Combined list of results
        """
        ticker_map = {}  # Maps ticker to combined stock data
        
        for provider, provider_results in results.items():
            for stock in provider_results:
                ticker = stock.get("ticker")
                if not ticker:
                    continue
                
                if ticker not in ticker_map:
                    # Add provider information
                    stock["providers"] = [provider]
                    ticker_map[ticker] = stock
                else:
                    # Merge data from this provider into existing entry
                    existing = ticker_map[ticker]
                    existing["providers"].append(provider)
                    
                    # Merge other fields, preferring non-None values
                    for key, value in stock.items():
                        if key != "providers" and value is not None:
                            if key not in existing or existing[key] is None:
                                existing[key] = value
        
        return list(ticker_map.values())
    
    def filter_by_risk(self, stocks: List[Dict[str, Any]], risk_level: str) -> List[Dict[str, Any]]:
        """
        Filter stocks based on risk level.
        
        Args:
            stocks: List of stocks to filter
            risk_level: Risk level ('low', 'medium', 'high')
            
        Returns:
            Filtered list of stocks
        """
        filtered = []
        
        for stock in stocks:
            if risk_level.lower() == 'low':
                # Low risk criteria: large cap, low debt, steady dividend
                if (stock.get('marketCap', 0) > 500_000_000_000 and
                    stock.get('debtToEquity', float('inf')) < 0.3 and
                    stock.get('dividendYield', 0) > 1.0):
                    filtered.append(stock)
                    
            elif risk_level.lower() == 'medium':
                # Medium risk criteria: mid cap, moderate debt
                if (50_000_000_000 < stock.get('marketCap', 0) < 500_000_000_000 and
                    stock.get('debtToEquity', float('inf')) < 1.0):
                    filtered.append(stock)
                    
            elif risk_level.lower() == 'high':
                # High risk criteria: small cap or high growth
                if (stock.get('marketCap', 0) < 50_000_000_000 or
                    stock.get('peRatio', 0) > 30):  # High P/E often indicates growth expectations
                    filtered.append(stock)
                    
            else:
                logger.warning(f"Unknown risk level: {risk_level}")
                return stocks  # Return all stocks if risk level is unknown
        
        return filtered
    
    def get_top_k(self, stocks: List[Dict[str, Any]], k: int, sort_by: str = 'marketCap', 
                 reverse: bool = True) -> List[Dict[str, Any]]:
        """
        Get the top K stocks based on a sorting criterion.
        
        Args:
            stocks: List of stocks to filter
            k: Number of stocks to return
            sort_by: Field to sort by
            reverse: Whether to sort in descending order
            
        Returns:
            Top K stocks
        """
        def get_sort_value(stock):
            value = stock.get(sort_by)
            return value if value is not None else float('-inf') if reverse else float('inf')
        
        sorted_stocks = sorted(stocks, key=get_sort_value, reverse=reverse)
        return sorted_stocks[:k]
    
    def get_stock_details_from_multiple_sources(self, ticker: str, 
                                              providers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get detailed information for a stock from multiple providers and combine the results.
        
        Args:
            ticker: Stock ticker symbol
            providers: List of provider names to use (uses all providers if None)
            
        Returns:
            Combined detailed information
        """
        providers = providers or list(self.screeners.keys())
        details = {}
        
        for provider in providers:
            if provider not in self.screeners:
                continue
                
            try:
                provider_details = self.screeners[provider].get_stock_details(ticker)
                
                # Record the provider
                if provider_details:
                    provider_details["provider"] = provider
                    
                # If we don't have any details yet, use these as our base
                if not details:
                    details = provider_details
                else:
                    # Merge provider-specific data under a provider key
                    details[f"{provider}_data"] = provider_details
                    
                    # Merge top-level fields, preferring existing non-None values
                    for key, value in provider_details.items():
                        if key != "provider" and value is not None:
                            if key not in details or details[key] is None:
                                details[key] = value
                                
            except Exception as e:
                logger.error(f"Error fetching details for {ticker} from {provider}: {str(e)}")
        
        return details 
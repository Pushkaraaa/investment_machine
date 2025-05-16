"""
Example usage of the screener tools.
"""
import os
import logging
import json
from typing import Dict, Any

from .factory import get_screener, get_screener_utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def pretty_print(data: Dict[str, Any]) -> None:
    """Print data in a readable format."""
    print(json.dumps(data, indent=2, default=str))

def main():
    """Main example function."""
    # Get API key from environment variable or replace with your API key
    finology_api_key = os.environ.get("FINOLOGY_API_KEY", "your_api_key_here")
    
    # Example 1: Using a single screener directly
    logger.info("Example 1: Using a single screener")
    finology = get_screener("finology", api_key=finology_api_key)
    if finology:
        # Get available criteria
        criteria = finology.get_available_criteria()
        logger.info(f"Available criteria: {', '.join(criteria.keys())}")
        
        # Perform a screen
        logger.info("Screening for large cap technology stocks...")
        results = finology.screen({
            "sector": "Technology",
            "marketCapMin": 500_000_000_000,  # 500B INR
            "exchange": "NSE",
            "limit": 5
        })
        
        # Display results
        logger.info(f"Found {len(results)} matching stocks:")
        for stock in results:
            pretty_print(stock)
            
        # Get details for a single stock (if results exist)
        if results:
            ticker = results[0].get("ticker")
            logger.info(f"Getting details for {ticker}...")
            details = finology.get_stock_details(ticker)
            pretty_print(details)
    
    # Example 2: Using multiple screeners with ScreenerUtils
    logger.info("\nExample 2: Using ScreenerUtils with multiple screeners")
    
    # For this example we'll just use Finology, but in a real scenario you would
    # configure multiple providers
    screener_configs = {
        "finology": {"api_key": finology_api_key}
    }
    
    utils = get_screener_utils(screener_configs=screener_configs)
    
    # Screen with all providers
    logger.info("Screening for dividend stocks with all providers...")
    results_by_provider = utils.screen_parallel({
        "dividendYieldMin": 2.0,
        "marketCapMin": 100_000_000_000,  # 100B INR
        "limit": 10
    })
    
    # Combine and process results
    combined_results = utils.combine_results(results_by_provider)
    logger.info(f"Found {len(combined_results)} unique stocks across all providers")
    
    # Filter by risk
    low_risk_stocks = utils.filter_by_risk(combined_results, "low")
    logger.info(f"Found {len(low_risk_stocks)} low-risk dividend stocks")
    
    # Get top 3 by market cap
    top_stocks = utils.get_top_k(low_risk_stocks, 3, sort_by="marketCap")
    logger.info("Top 3 low-risk dividend stocks by market cap:")
    for stock in top_stocks:
        pretty_print(stock)
    
    # Get detailed information for the top stock
    if top_stocks:
        ticker = top_stocks[0].get("ticker")
        logger.info(f"Getting detailed information for {ticker} from all sources...")
        details = utils.get_stock_details_from_multiple_sources(ticker)
        pretty_print(details)

if __name__ == "__main__":
    main() 
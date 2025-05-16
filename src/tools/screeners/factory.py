"""
Factory for creating screener instances.
"""
from typing import Dict, Optional, Type, List
import logging

from .base_screener import BaseScreener
from .finology_screener import FinologyScreener
from .eodhd_screener import EODHDScreener
from .screener_utils import ScreenerUtils

logger = logging.getLogger(__name__)

# Registry of available screeners
SCREENERS: Dict[str, Type[BaseScreener]] = {
    "finology": FinologyScreener,
    "eodhd": EODHDScreener,
    # Add other screeners as they are implemented
    # "screener.in": ScreenerIn,
    # "tickertape": TickerTape,
    # "trade_brains": TradeBrains,
    # "investing.com": InvestingCom,
}

def get_screener(provider: str, **kwargs) -> Optional[BaseScreener]:
    """
    Get a screener instance for the specified provider.
    
    Args:
        provider: Name of the screener provider
        **kwargs: Additional arguments to pass to the screener constructor
        
    Returns:
        An instance of the requested screener, or None if the provider is not supported
    """
    screener_class = SCREENERS.get(provider.lower())
    if not screener_class:
        logger.error(f"Screener provider '{provider}' not supported.")
        logger.info(f"Available providers: {', '.join(SCREENERS.keys())}")
        return None
    
    try:
        return screener_class(**kwargs)
    except Exception as e:
        logger.error(f"Error creating screener instance: {str(e)}")
        return None

def get_screener_utils(providers: Optional[List[str]] = None, 
                     screener_configs: Optional[Dict[str, Dict]] = None) -> ScreenerUtils:
    """
    Get a ScreenerUtils instance with multiple screeners configured.
    
    Args:
        providers: List of provider names to initialize (uses all available if None)
        screener_configs: Dictionary mapping provider names to their configuration parameters
            Example: {"finology": {"api_key": "your_api_key"}, "eodhd": {"api_token": "your_token"}}
        
    Returns:
        A ScreenerUtils instance with the requested screeners
    """
    utils = ScreenerUtils()
    providers = providers or list(SCREENERS.keys())
    screener_configs = screener_configs or {}
    
    for provider in providers:
        config = screener_configs.get(provider, {})
        screener = get_screener(provider, **config)
        if screener:
            utils.add_screener(provider, screener)
    
    return utils 
"""
Base screener interface that all screener implementations should inherit from.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseScreener(ABC):
    """Base class for all stock screeners."""
    
    @abstractmethod
    def screen(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Screen stocks based on given criteria.
        
        Args:
            criteria: Dictionary of screening criteria with parameter names and values
                     Specific criteria keys will depend on the screener implementation
        
        Returns:
            List of dictionaries containing stock information that matches the criteria
        """
        pass
    
    @abstractmethod
    def get_available_criteria(self) -> Dict[str, Any]:
        """
        Get available screening criteria for this screener.
        
        Returns:
            Dictionary mapping criteria names to their possible values or ranges
        """
        pass
    
    @abstractmethod
    def get_stock_details(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing detailed stock information
        """
        pass 
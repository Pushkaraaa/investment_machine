# Data Fetchers

This directory contains tools for fetching financial data from various sources.

## Alpha Vantage Client

The `alpha_vantage.py` module provides a client for interacting with the Alpha Vantage API to retrieve:
- Stock time series data
- Fundamental data (company overview, income statements, balance sheets, cash flow)
- News and sentiment analysis
- Calculated financial metrics

### Implementation Note

While the project's `requirements.txt` includes the `alpha_vantage` Python package, our implementation uses direct REST API calls instead. This approach was chosen for several reasons:

1. **Flexibility**: Direct API calls provide more control over request parameters and error handling
2. **Up-to-date Endpoints**: The official package may not always support the latest Alpha Vantage API features
3. **Customization**: Our implementation adds additional helper methods for common financial analysis tasks
4. **Performance**: Direct requests can be more efficient for our specific use cases

### Usage Example

```python
from investment_machine.src.tools.data_fetchers import AlphaVantageClient

# Initialize the client
client = AlphaVantageClient()  # API key from environment variable
# or
client = AlphaVantageClient(api_key="YOUR_API_KEY")

# Get daily adjusted data
df = client.get_daily_adjusted("RELIANCE.NS")

# Get company fundamentals
overview = client.get_company_overview("RELIANCE.NS")
income_stmt = client.get_income_statement("RELIANCE.NS")
balance_sheet = client.get_balance_sheet("RELIANCE.NS")
cash_flow = client.get_cash_flow("RELIANCE.NS")

# Get news and sentiment
news = client.get_news_sentiment(symbol="RELIANCE.NS", limit=10)

# Calculate key financial metrics
metrics = client.calculate_key_metrics("RELIANCE.NS")
```

For more detailed examples, see the Jupyter notebook at `investment_machine/notebooks/alpha_vantage_demo.ipynb`.

## Adding More Data Fetchers

Follow this pattern when adding new data source integrations:
1. Create a new module for the data source (e.g., `upstox.py`)
2. Implement a client class with methods for different data endpoints
3. Update the `__init__.py` file to expose the new client
4. Add examples of usage in a Jupyter notebook
5. Update this README with information about the new data fetcher 
# Investment Machine

## Overview
An advanced multi-agent investment bot leveraging LangGraph for India-focused financial analysis and automated trading. This system uses retrieval-augmented generation (RAG), daily news ingestion, and specialized agents to create a comprehensive investment workflow.

## Features
- Multi-agent architecture with specialized roles (CIO, Analysts, Traders, etc.)
- News & sentiment analysis with RAG for contextual market understanding
- Fundamental analysis, technical analysis, and portfolio management
- Risk categorization and management
- Institutional holdings tracking
- Seasonal market pattern analysis
- Human-in-the-loop oversight for critical decisions

## Project Structure
```
investment_machine/
├── config/                     # Configuration files
│   ├── settings.py             # Core settings and parameters
│   ├── logging_config.py       # Logging configuration
│   └── agent_config.py         # Agent-specific configurations
│
├── data/                       # Data storage
│   ├── raw/                    # Raw data from APIs
│   ├── processed/              # Processed data ready for analysis
│   └── vector_store/           # Vector embeddings for RAG
│
├── src/                        # Source code
│   ├── agents/                 # LangGraph agents
│   │   ├── base_agent.py       # Base agent class
│   │   ├── cio/                # Chief Investment Officer agents
│   │   ├── analysts/           # Analyst agents (Fundamental, Technical, etc.)
│   │   ├── news/               # News and sentiment analysis agents
│   │   ├── market_research/    # Market research and screening agents
│   │   ├── quant/              # Quantitative analysis agents
│   │   ├── risk/               # Risk management agents
│   │   ├── portfolio/          # Portfolio management agents
│   │   └── trading/            # Execution and trading agents
│   │
│   ├── pipelines/              # Data and workflow pipelines
│   │   ├── ingestion/          # Data ingestion pipelines
│   │   ├── analysis/           # Analysis pipelines
│   │   ├── recommendation/     # Recommendation generation pipelines
│   │   └── execution/          # Trade execution pipelines
│   │
│   ├── tools/                  # Tools used by agents
│   │   ├── data_fetchers/      # API integrations (Alpha Vantage, yfinance, etc.)
│   │   ├── screeners/          # Stock screening tools
│   │   ├── calculators/        # Financial calculators and metrics
│   │   ├── rag/                # RAG implementation
│   │   └── brokers/            # Broker API connectors (Upstox, etc.)
│   │
│   ├── utils/                  # Utility functions
│   │   ├── validators.py       # Data validation utilities
│   │   ├── formatters.py       # Data formatting utilities
│   │   ├── date_utils.py       # Date handling utilities
│   │   └── metrics.py          # Performance metrics utilities
│   │
│   └── core/                   # Core system components
│       ├── graph_builder.py    # LangGraph builder
│       ├── state_manager.py    # State management
│       ├── memory.py           # Memory implementation
│       └── security.py         # Security and authentication
│
├── tests/                      # Test suite
│   ├── agents/                 # Tests for agents
│   ├── pipelines/              # Tests for pipelines
│   ├── tools/                  # Tests for tools
│   └── utils/                  # Tests for utilities
│
├── notebooks/                  # Jupyter notebooks for exploration and visualization
│
├── scripts/                    # Utility scripts
│   ├── setup.py                # Setup script
│   └── backtest.py             # Backtesting script
│
├── resources/                  # Documentation and resources
│   └── agentic_architecture.md # Architecture documentation
│
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
└── .env.example                # Example environment variables
```

## Key Components

### Agents
The system is built around a team of specialized agents that collaborate like different departments in an investment firm:

1. **Chief Investment Officer (CIO) Agent**: The central orchestrator that sets strategy and coordinates other agents
2. **Market Research & Screening Agents**: Identify potential investment opportunities
3. **Fundamental Analysis Agents**: Perform in-depth analysis of company financials and business models
4. **Quantitative Analysis Agents**: Develop and apply quantitative models and signals
5. **News & Sentiment Analysis Agents**: Process and analyze financial news and market sentiment
6. **Risk Management Agents**: Monitor portfolio risk and ensure compliance with risk guidelines
7. **Portfolio Management Agents**: Construct and manage the investment portfolio
8. **Execution Trading Agents**: Execute trades through broker APIs

### Pipelines
The system uses several key data and workflow pipelines:

1. **Data Ingestion Pipeline**: Fetch and update market data, fundamentals, news, and institutional flows
2. **Opportunity Identification Pipeline**: Screen and identify potential investment candidates
3. **Analysis Pipeline**: Perform in-depth analysis on selected securities
4. **Portfolio Construction Pipeline**: Optimize portfolio allocation based on recommendations
5. **Trade Execution Pipeline**: Place and manage orders through broker APIs
6. **Monitoring Pipeline**: Track portfolio performance and market conditions

### RAG Implementation
The system leverages Retrieval-Augmented Generation to provide agents with up-to-date, domain-specific context:

1. **Knowledge Base**: Ingest news articles, company filings, analyst reports, and economic data
2. **Vector Embeddings**: Convert data into vector embeddings stored in a vector database
3. **Contextual Retrieval**: Retrieve relevant information based on agent queries
4. **Enhanced Generation**: Augment LLM responses with retrieved context for more accurate analysis

## Getting Started

### Prerequisites
- Python 3.10+
- Required API keys (add to .env file):
  - OpenAI API key
  - Alpha Vantage API key
  - Upstox API credentials
  - Other data provider keys

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/investment_machine.git
cd investment_machine

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the System
```bash
# Start the main system
python main.py

# Run specific pipeline
python -m src.pipelines.ingestion.news_ingestion

# Run tests
pytest
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 
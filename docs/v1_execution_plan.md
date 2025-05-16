# Project Plan

## Phase 1: Core Infrastructure & Basic Tools (2–3 weeks)

- **Set up project structure**
  - Initialize the repository with the structure from `README.md`
  - Configure environment & dependencies

- **Implement basic data fetchers**
  - Integrate `yfinance` for stock data
  - Alpha Vantage API connector for fundamentals
  - Simple news API integration (Alpha Vantage News & Sentiments)

- **Build fundamental analysis tools**
  - Create calculators for key ratios (P/E, P/B, ROE, etc.)
  - Implement industry comparison utilities

- **Set up basic screener functionality**

- **Develop minimal state management**
  - Simple portfolio tracking
  - Basic persistence layer

---

## Phase 2: First Agent Implementation (2–3 weeks)

- **Build the Fundamental Analyst Agent**
  - Connect to fundamental data tools
  - Implement analysis workflows
  - Create basic recommendation generation

- **Set up simple RAG system**
  - Implement vector store with company information
  - Create ingestion pipeline for financial reports
  - Build simple query mechanisms

- **Implement basic CIO agent**
  - Coordinate with Fundamental Analyst
  - Maintain basic portfolio state
  - Generate simple investment theses

- **Create minimal UI/output format**
  - Structured recommendation output
  - Basic visualization of analysis

---

## Phase 3: MVP Integration & Testing (2 weeks)

- **Integrate agents into a simple workflow**
  - Stock screening → Fundamental Analysis → Recommendation
  - Human review interface

- **Implement basic risk categorization**
  - Simple risk scoring based on volatility and fundamentals
  - Portfolio allocation suggestions

- **Testing and validation**
  - Backtest on historical data
  - Compare recommendations against expert opinions

- **Documentation and refinement**
  - Document API usage
  - Create example workflows

---

## MVP Features

Your MVP should include:

- Data ingestion from key sources (`Alpha Vantage`, `yfinance`)
- Basic fundamental analysis capabilities (ratio calculation, peer comparison)
- Simple RAG implementation for financial reports and news
- Two core agents: **Fundamental Analyst** and **basic CIO**
- Risk categorization of stocks into buckets
- Human-in-the-loop review interface
- Basic reporting of recommendations and rationale

---

This approach lets you validate the core architecture while delivering immediate value.  
You can then expand with additional agents and more sophisticated analyses in future iterations.

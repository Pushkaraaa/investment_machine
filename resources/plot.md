graph TD
    %% External Data & APIs Subgraph
    subgraph External Data and APIs
        direction LR
        MD_API["Market Data APIs <br/> Upstox, yfinance"]
        FD_API["Fundamental Data APIs <br/> Alpha Vantage"]
        NEWS_API["News APIs <br/> Alpha Vantage News"]
        INST_API["Institutional Data APIs <br/> NSE BSE Trackers"]
        ECON_API["Economic Data APIs"]
        VDB[("Vector Database <br/> Pinecone Milvus")] 
        BROKER_API["Broker API <br/> Upstox Trading API"]
    end

    %% Human Supervision Subgraph
    subgraph Human Supervision
        HITL["Human in the Loop <br/> Review and Approval"]
    end

    %% CIO - Central Orchestrator
    subgraph Core Orchestration and Strategy
        CIO["Chief Investment Officer CIO Agent <br/> Orchestrator and Strategist"]
    end

    %% Layer 1: Monitoring & Screening Agents/Teams
    subgraph Layer 1 Monitoring and Screening
        direction TB
        subgraph Market Research and Screening Team
            JA["Junior Analyst Agents <br/> Screeners"]
            SS["Sector Specialist Agents"]
        end
        NEWS_FLOW_MONITOR["News Fetcher and FII DII Flow Monitor Agent"]

        %% Data to Layer 1
        MD_API --> JA
        NEWS_API --> NEWS_FLOW_MONITOR
        INST_API --> NEWS_FLOW_MONITOR

        %% Layer 1 to CIO & Inter-Layer 1
        JA -- "Flagged Stocks and Initial Screens" --> CIO
        JA -- "Flagged Stocks for Sector Context" --> SS
        NEWS_FLOW_MONITOR -- "Key News and Flow Alerts" --> CIO
        NEWS_FLOW_MONITOR -- "Contextual News or Flows for Sector" --> SS
    end

    %% Layer 2: Deep Evaluation & Due Diligence Agents/Teams
    subgraph Layer 2 Deep Evaluation and Due Diligence
        direction TB
        subgraph Fundamental Analysis Team
            FA["Fundamental Analyst Agent"]
        end
        subgraph "News, Sentiment and Institutional Desk"
            direction TB
            NEWS_RAG["News Aggregator and RAG Agent"]
            INST_WATCH["Institutional Watch Agent"]
        end
        subgraph Quantitative Strategy Team
            ALPHA_GEN["Alpha Generation Agent"]
        end
        SE_ECON["Seasonal and Economic Analysis Agent"]

        %% Data to Layer 2 Agents
        FD_API --> FA
        NEWS_API --> NEWS_RAG
        VDB --> NEWS_RAG 
        INST_API --> INST_WATCH
        VDB --> INST_WATCH 
        MD_API --> ALPHA_GEN
        ECON_API --> SE_ECON
        MD_API --> SE_ECON 

        %% CIO & SS Tasking/Interacting with Layer 2
        CIO -- "Task Strategic Deep Dives" --> SS
        CIO -- "Task Fundamental Analysis for Stock X" --> FA
        CIO -- "Task News Sentiment RAG for Topic Y" --> NEWS_RAG
        CIO -- "Task Institutional Activity Check for Entity Z" --> INST_WATCH
        CIO -- "Task Quantitative Model RD and Signal Evaluation" --> ALPHA_GEN
        CIO -- "Task Macro Seasonal Outlook Update" --> SE_ECON

        SS -- "Request Detailed Fundamental Analysis for Sector Stock" --> FA
        SS -- "Request Sector Specific News Sentiment via RAG" --> NEWS_RAG
        SS -- "Request Sector Specific Institutional Insights" --> INST_WATCH
        SS -- "Request Quant Insights for Sector Stocks" --> ALPHA_GEN
        SS -- "Request Macro Seasonal Context for Sector" --> SE_ECON

        %% Layer 2 Reporting to CIO & PM (Portfolio Manager)
        FA -- "Fundamental Thesis, Valuation, Recs" --> CIO
        NEWS_RAG -- "Contextual News Sentiment Insights RAG" --> CIO
        INST_WATCH -- "Institutional Movement Insights and Recs" --> CIO
        ALPHA_GEN -- "Quantitative Signals, Models and Recs" --> CIO
        SE_ECON -- "Macro and Seasonal Insights, Strategic Recs" --> CIO
        SS -- "Consolidated Sector Theses and Stock Recs" --> CIO

        FA -- "Input to Portfolio Construction" --> PM
        NEWS_RAG -- "Input to Portfolio Construction" --> PM
        INST_WATCH -- "Input to Portfolio Construction" --> PM
        ALPHA_GEN -- "Input to Portfolio Construction" --> PM
        SE_ECON -- "Input to Portfolio Construction" --> PM
        SS -- "Input to Portfolio Construction" --> PM
    end

    %% Layer 3: Portfolio Management & Execution Agents/Teams
    subgraph Layer 3 Portfolio Management and Execution
        direction TB
        RISK_MGMT["Risk Management Agent"]
        PM["Portfolio Manager Agent <br/> Incl State Management"]
        ET["Execution Trader Agent"]

        %% Data to Layer 3 Agents
        MD_API --> RISK_MGMT 
        PM -- "Live Portfolio State" --> RISK_MGMT 

        %% CIO and Layer 2 to Layer 3
        CIO -- "Overall Strategy, Risk Mandates, Final Decisions" --> PM
        CIO -- "Set Risk Policy and Oversight" --> RISK_MGMT

        RISK_MGMT -- "Risk Reports, Alerts, Compliance Checks" --> CIO
        RISK_MGMT -- "Risk Limits and Portfolio Risk Feedback" --> PM

        PM -- "Proposed Trades or Portfolio Adjustments Pre Approval" --> HITL
        HITL -- "Approved Trades or Strategic Adjustments" --> PM
        PM -- "Execute Approved Trades and Manage Portfolio" --> ET
        PM -- "Portfolio State and Performance Reports" --> CIO

        ET -- "Trade Execution Orders" --> BROKER_API
        BROKER_API -- "Trade Fills and Market Data for Execution" --> ET
        ET -- "Execution Confirmations and Status Updates" --> PM
    end

    %% General Interactions with Human Supervision
    CIO -- "Request Manual Review or Strategic Approval" --> HITL
    HITL -- "Strategic Decisions, Overrides or Approvals" --> CIO

    %% Styling
    classDef data fill:#e6e6fa,stroke:#444,stroke-width:1.5px,color:#333;
    classDef agent fill:#d1fecb,stroke:#444,stroke-width:1.5px,color:#333;
    classDef team_group fill:#f0f8ff,stroke:#666,stroke-width:2px,rx:10px,ry:10px,color:#333;
    classDef cio fill:#fffacd,stroke:#555,stroke-width:2px,color:#333;
    classDef hitl fill:#ffe4c4,stroke:#555,stroke-width:2px,color:#333;

    class MD_API,FD_API,NEWS_API,INST_API,ECON_API,VDB,BROKER_API data;
    class JA,SS,NEWS_FLOW_MONITOR,FA,NEWS_RAG,INST_WATCH,ALPHA_GEN,SE_ECON,RISK_MGMT,PM,ET agent;
    class CIO cio;
    class HITL hitl;

    class "Market Research and Screening Team","Fundamental Analysis Team","News, Sentiment and Institutional Desk","Quantitative Strategy Team", "Core Orchestration and Strategy", "Human Supervision", "External Data and APIs" team_group;
    class "Layer 1 Monitoring and Screening", "Layer 2 Deep Evaluation and Due Diligence", "Layer 3 Portfolio Management and Execution" team_group;
# Financial Ledger & Budget Application

## Overview
A web-based financial tracking application deployed via Streamlit. The system executes transaction logic (deposits, withdrawals, transfers) across different category ledgers and visualizes spending distributions dynamically.

## System Architecture

The application is structured on two core layers:

1.  **Data Layer (Object-Oriented Logic):** 
    Operates via a Python `Category` class. It manages state mutations (appending transactions to a ledger) and executes real-time balance validations before authorizing withdrawals. 
2.  **Presentation Layer (Streamlit UI):** 
    Utilizes Streamlit's `session_state` to persist data across user interactions. It maps the internal dictionary states to native Pandas DataFrames and UI components for immediate visualization.

## Technical Stack
*   **Language:** Python 
*   **Framework:** Streamlit (UI & State Management)
*   **Data Handling:** Pandas (Tabular structuring and charting)

## Core Capabilities
*   **Transaction Execution:** Record deposits and validated withdrawals.
*   **State Persistence:** Maintains ledger history during active sessions.
*   **Balance Aggregation:** Real-time calculation of available funds per category.
*   **Visual Analytics:** Automated bar chart generation mapping relative spending distribution across categories.


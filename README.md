# Algo-Trading-and-Samsung-advisor

# Python Evaluation (Task 1 + Task 2)

This repo contains two separate projects for the evaluation:

- **Task 1:** Golden Cross Algorithmic Trading strategy (MA50/MA200) with a $5000 budget  
- **Task 2:** Samsung Phone Advisor (PostgreSQL + FastAPI) using GSMArena data + rule-based responses

## Folder Structure
Task-1-Algorithmic-Trading/
Task-2-Samsung-Phone-Advisor/

## Requirements
- Python 3.10+
- VS Code / Jupyter Notebook
- Internet (Task 1 uses yfinance; Task 2 scraping optional if using CSV seed)
- PostgreSQL (for Task 2)

---

## Task 1 — Algorithmic Trading Adventure
Go to: `Task-1-Algorithmic-Trading/`

Run the notebook and execute all cells.  
It downloads data with `yfinance`, cleans it, calculates MA50/MA200, trades on golden/death cross, force closes at the end, and prints trades + final P/L + a plot.

---

## Task 2 — Samsung Phone Advisor
Go to: `Task-2-Samsung-Phone-Advisor/`

### PostgreSQL
Create a database named `samsung`.

Default connection used:
`postgresql+psycopg2://postgres:postgres@localhost:5432/samsung`

### Run the API
Inside the Task 2 folder:
```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload

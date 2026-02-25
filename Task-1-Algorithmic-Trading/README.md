# Task 1 — Golden Cross Trading Strategy

This notebook implements a simple moving-average crossover strategy:

- MA50 and MA200
- Buy on golden cross (MA50 crosses above MA200)
- Sell on death cross (MA50 crosses below MA200)
- $5000 fixed budget (max shares only)
- One open position at a time
- Force close on the last day
- Outputs: trades, P/L summary, and a chart

## How to run
1. Open `Task-1_yfinance.ipynb`
2. Run all cells top to bottom

If you run it again, it will reuse the cached CSV inside `./data/`.

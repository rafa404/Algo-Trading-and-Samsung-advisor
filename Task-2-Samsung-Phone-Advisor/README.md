# Task 2 — Samsung Phone Advisor (PostgreSQL + FastAPI)

This project is a small assistant that answers Samsung phone questions using:
- **PostgreSQL** for structured specs (RAG-style lookup)
- A simple **two-step flow**:
  - Data Extractor (SQL fetch)
  - Review/Recommendation Generator (rule-based text)
- **FastAPI** with one endpoint: `POST /ask`
- A clean demo UI at `/`

---

## Requirements
- Python
- PostgreSQL running locally

Default DB connection used in `app.py`:
`postgresql+psycopg2://postgres:postgres@localhost:5432/samsung`

---

## 1) Create Database
Create a database named `samsung` in PostgreSQL.

---

## 2) Load Phone Data (Recommended: CSV Seed)
This repo includes `phones_seed.csv` so you can load data without scraping.

### Option A: Load using notebook
Open `database set.ipynb` and run the **CSV seed cell** (it creates the table and inserts rows).

### Option B: Scrape GSMArena
`database set.ipynb` also contains the scraper that collects ~20–30 Samsung models from GSMArena and inserts them into PostgreSQL.

---

## 3) Install + Run API
From inside this folder:

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
````

Open:

* UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Example Questions

Try these in the UI or via `/docs`:

* `What are the specs of Samsung Galaxy S23 Ultra?`
* `Compare Galaxy S23 Ultra and S22 Ultra for photography`
* `Which Samsung phone has the best battery under $1000?`

---

## API Example

Request:

```json
{ "question": "Compare Galaxy S23 Ultra and S22 Ultra for photography" }
```

Response:

```json
{ "answer": "..." }
```

```
```


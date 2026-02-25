import os
import re
from difflib import get_close_matches
from fastapi.responses import HTMLResponse

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/samsung",
)

engine = create_engine(DATABASE_URL, future=True)
app = FastAPI(title="Samsung Phone Advisor")


class AskRequest(BaseModel):
    question: str


MODELS = []


@app.on_event("startup")
def load_models():
    global MODELS
    with engine.connect() as conn:
        MODELS = [r[0] for r in conn.execute(text("SELECT model_name FROM phones")).fetchall()]


def match_model(name: str):
    name = (name or "").strip()
    hit = get_close_matches(name, MODELS, n=1, cutoff=0.3)
    return hit[0] if hit else None


def fetch_one(model_name: str):
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT model_name, release_date, display, battery, camera, ram, storage, price
                FROM phones
                WHERE model_name = :m
                """
            ),
            {"m": model_name},
        ).mappings().first()
    return dict(row) if row else None


def fetch_all():
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT model_name, release_date, display, battery, camera, ram, storage, price
                FROM phones
                """
            )
        ).mappings().all()
    return [dict(r) for r in rows]


def format_specs(p: dict):
    return (
        f"{p['model_name']} specs:\n"
        f"- Release: {p.get('release_date')}\n"
        f"- Display: {p.get('display')}\n"
        f"- Battery: {p.get('battery')}\n"
        f"- Camera: {p.get('camera')}\n"
        f"- RAM: {p.get('ram')}\n"
        f"- Storage: {p.get('storage')}\n"
        f"- Price: {p.get('price')}\n"
    )


def compare_text(p1: dict, p2: dict, focus: str = ""):
    out = [f"Comparison: {p1['model_name']} vs {p2['model_name']}"]

    if "camera" in focus or "photo" in focus:
        out.append(
            f"- Camera:\n"
            f"  {p1['model_name']}: {p1.get('camera')}\n"
            f"  {p2['model_name']}: {p2.get('camera')}"
        )
        out.append("Recommendation: For photography, prefer the phone with stronger camera specs.")

    out.append(
        f"- Battery:\n"
        f"  {p1['model_name']}: {p1.get('battery')}\n"
        f"  {p2['model_name']}: {p2.get('battery')}"
    )
    out.append("Overall: For longer usage, prefer the phone with bigger battery capacity (mAh) in specs.")

    return "\n".join(out)


def extract_budget(q: str):
    m = re.search(r"(under|below)\s*\$?\s*(\d+)", q.lower())
    return int(m.group(2)) if m else None


def extract_price_number(price_text):
    if not price_text:
        return None
    m = re.search(r"(\d{3,5})", str(price_text).replace(",", ""))
    return int(m.group(1)) if m else None


def battery_num(btxt):
    m = re.search(r"(\d{4,6})\s*mAh", str(btxt), re.I)
    return int(m.group(1)) if m else 0


def answer_question(question: str):
    q = (question or "").strip()
    ql = q.lower()

    if "spec" in ql:
        name = q.replace("specs of", "").replace("Specs of", "").strip()
        m = match_model(name)
        if not m:
            return "Model not found in database."
        p = fetch_one(m)
        return format_specs(p) if p else "Model not found in database."

    if "compare" in ql or " vs " in ql:
        if " vs " in q:
            left, right = q.split(" vs ", 1)
            left = left.replace("compare", "").replace("Compare", "").strip()
            right = right.strip()
        elif " and " in q:
            left, right = q.split(" and ", 1)
            left = left.replace("compare", "").replace("Compare", "").strip()
            right = right.strip()
        else:
            return "Ask like: Compare Galaxy S23 Ultra and S22 Ultra for photography."

        m1, m2 = match_model(left), match_model(right)
        if not m1 or not m2:
            return "Could not match one or both models."

        p1, p2 = fetch_one(m1), fetch_one(m2)
        if not p1 or not p2:
            return "Could not load phone data from database."

        focus = "camera" if ("photo" in ql or "camera" in ql) else ""
        return format_specs(p1) + "\n" + format_specs(p2) + "\n" + compare_text(p1, p2, focus)

    if "best battery" in ql and ("under" in ql or "below" in ql):
        budget = extract_budget(q)
        if budget is None:
            return "Please ask like: Which Samsung phone has the best battery under $1000?"

        phones = fetch_all()
        candidates = []
        for p in phones:
            price_num = extract_price_number(p.get("price"))
            if price_num is not None and price_num <= budget:
                candidates.append(p)

        if not candidates:
            return "No phones found under that budget with a parseable price in this dataset."

        best = sorted(candidates, key=lambda x: battery_num(x.get("battery")), reverse=True)[0]
        return f"Best battery under ${budget}: {best['model_name']} ({best.get('battery')}, price: {best.get('price')})."

    return "Try: 'Specs of Galaxy S23 Ultra', 'Compare S23 Ultra and S22 Ultra', or 'best battery under $1000'."

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Samsung Phone Advisor</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0b0f17; color:#e8eefc; margin:0; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
    .card { background:#121a2a; border:1px solid #22304d; border-radius:14px; padding:18px; box-shadow: 0 10px 30px rgba(0,0,0,.25); }
    h1 { margin: 0 0 8px; font-size: 22px; }
    .sub { opacity:.8; margin-bottom:16px; }
    .row { display:flex; gap:10px; margin-top:12px; }
    input { flex:1; padding:12px 14px; border-radius:10px; border:1px solid #2a3a5d; background:#0f1626; color:#e8eefc; outline:none; }
    button { padding:12px 14px; border-radius:10px; border:1px solid #2a3a5d; background:#2b65ff; color:white; cursor:pointer; }
    button:disabled { opacity:.6; cursor:not-allowed; }
    .chips { display:flex; gap:8px; flex-wrap:wrap; margin: 12px 0 4px; }
    .chip { font-size: 12px; padding:8px 10px; border-radius:999px; border:1px solid #2a3a5d; background:#0f1626; cursor:pointer; opacity:.9; }
    .chat { margin-top:16px; display:flex; flex-direction:column; gap:10px; }
    .msg { padding:12px 14px; border-radius:12px; border:1px solid #22304d; white-space: pre-wrap; line-height:1.35; }
    .user { background:#0f1626; align-self:flex-end; max-width:85%; }
    .bot { background:#121a2a; align-self:flex-start; max-width:85%; }
    .meta { font-size:12px; opacity:.7; margin-top:6px; }
    .footer { opacity:.65; font-size:12px; margin-top:12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Samsung Phone Advisor</h1>
      <div class="sub">Ask about specs, comparisons, or recommendations (powered by PostgreSQL + /ask).</div>

      <div class="chips">
        <div class="chip" onclick="quick('What are the specs of Samsung Galaxy S23 Ultra?')">Specs: S23 Ultra</div>
        <div class="chip" onclick="quick('Compare Galaxy S23 Ultra and S22 Ultra for photography')">Compare: S23 vs S22 (photo)</div>
        <div class="chip" onclick="quick('Which Samsung phone has the best battery under $1000?')">Best battery under $1000</div>
      </div>

      <div class="row">
        <input id="q" placeholder="Type your question…" />
        <button id="btn" onclick="send()">Ask</button>
      </div>

      <div class="chat" id="chat"></div>
      <div class="footer">Tip: Your API is still available at <b>/ask</b>. Swagger docs at <b>/docs</b>.</div>
    </div>
  </div>

  <script>
    const chat = document.getElementById("chat");
    const q = document.getElementById("q");
    const btn = document.getElementById("btn");

    function addMsg(text, who) {
      const div = document.createElement("div");
      div.className = "msg " + who;
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    function setLoading(on) {
      btn.disabled = on;
      btn.textContent = on ? "Thinking…" : "Ask";
    }

    function quick(text) {
      q.value = text;
      q.focus();
    }

    async function send() {
      const question = q.value.trim();
      if (!question) return;
      addMsg(question, "user");
      q.value = "";
      setLoading(true);

      try {
        const res = await fetch("/ask", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({question})
        });
        const data = await res.json();
        addMsg(data.answer || "No answer returned.", "bot");
      } catch (e) {
        addMsg("Error: could not reach the API. Is the server running?", "bot");
      } finally {
        setLoading(false);
      }
    }

    q.addEventListener("keydown", (e) => {
      if (e.key === "Enter") send();
    });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML

@app.post("/ask")
def ask(req: AskRequest):
    return {"answer": answer_question(req.question)}
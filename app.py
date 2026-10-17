from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import sqlite3
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("PULSEGUARD_DB", str(ROOT / "pulseguard.db")))
app = FastAPI(
    title="PulseGuard Z",
    description="Explainable hospital supply shortage early-warning prototype.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

SEED_ITEMS = [
    {"sku":"MED-001","name":"Normal saline 0.9%","category":"IV fluids","on_hand":420,"daily_use":78,"lead_days":4,"incoming_qty":120,"incoming_days":2,"criticality":5,"site":"Ward A"},
    {"sku":"MED-002","name":"Paracetamol 500 mg","category":"Analgesics","on_hand":1800,"daily_use":260,"lead_days":3,"incoming_qty":0,"incoming_days":None,"criticality":3,"site":"Central store"},
    {"sku":"MED-003","name":"Insulin regular","category":"Diabetes care","on_hand":96,"daily_use":22,"lead_days":5,"incoming_qty":40,"incoming_days":3,"criticality":5,"site":"Cold storage"},
    {"sku":"MED-004","name":"Sterile gloves (pairs)","category":"PPE","on_hand":2400,"daily_use":310,"lead_days":6,"incoming_qty":500,"incoming_days":4,"criticality":4,"site":"Central store"},
    {"sku":"MED-005","name":"Amoxicillin 500 mg","category":"Antibiotics","on_hand":340,"daily_use":95,"lead_days":4,"incoming_qty":0,"incoming_days":None,"criticality":4,"site":"Pharmacy"},
    {"sku":"MED-006","name":"Oxygen cylinder equivalent (L)","category":"Respiratory","on_hand":720,"daily_use":190,"lead_days":1,"incoming_qty":300,"incoming_days":1,"criticality":5,"site":"Emergency"},
    {"sku":"MED-007","name":"Syringes 5 mL","category":"Consumables","on_hand":1600,"daily_use":220,"lead_days":5,"incoming_qty":700,"incoming_days":3,"criticality":3,"site":"Central store"},
    {"sku":"MED-008","name":"ORS sachets","category":"Rehydration","on_hand":260,"daily_use":36,"lead_days":3,"incoming_qty":0,"incoming_days":None,"criticality":2,"site":"Pharmacy"},
    {"sku":"MED-009","name":"Pediatric antibiotic suspension","category":"Pediatrics","on_hand":72,"daily_use":18,"lead_days":6,"incoming_qty":24,"incoming_days":4,"criticality":5,"site":"Pediatric ward"},
    {"sku":"MED-010","name":"N95 masks","category":"PPE","on_hand":680,"daily_use":115,"lead_days":4,"incoming_qty":300,"incoming_days":2,"criticality":4,"site":"Emergency"},
]

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
          sku TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
          on_hand REAL NOT NULL, daily_use REAL NOT NULL, lead_days INTEGER NOT NULL,
          incoming_qty REAL NOT NULL DEFAULT 0, incoming_days INTEGER,
          criticality INTEGER NOT NULL, site TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )""")
        count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            conn.executemany("""
            INSERT INTO inventory VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, [
                (x["sku"],x["name"],x["category"],x["on_hand"],x["daily_use"],
                 x["lead_days"],x["incoming_qty"],x["incoming_days"],x["criticality"],
                 x["site"],now) for x in SEED_ITEMS
            ])

@app.on_event("startup")
def startup():
    init_db()

def score_item(row):
    item = dict(row)
    daily_use = max(float(item["daily_use"]), 0.01)
    stock_days = float(item["on_hand"]) / daily_use
    lead_days = int(item["lead_days"])
    incoming_qty = float(item["incoming_qty"])
    incoming_days = item["incoming_days"]
    delivery_covers_gap = incoming_qty >= daily_use * max(0.0, lead_days - (float(incoming_days) if incoming_days is not None else lead_days))
    exposure = max(0.0, min(1.0, (lead_days + 2 - stock_days) / max(lead_days + 2, 1)))
    criticality_factor = float(item["criticality"]) / 5.0
    score = round(min(100, max(0, 100 * (0.72 * exposure + 0.28 * criticality_factor))), 1)
    if incoming_qty > 0 and incoming_days is not None and incoming_days < stock_days:
        score = round(max(0, score - min(22, incoming_qty / daily_use * 3)), 1)
    if score >= 72:
        level = "CRITICAL"
    elif score >= 52:
        level = "HIGH"
    elif score >= 32:
        level = "MEDIUM"
    else:
        level = "LOW"
    reorder_target = daily_use * (lead_days + 5)
    recommended_order = max(0, round(reorder_target - float(item["on_hand"]) - incoming_qty))
    reasons = []
    if stock_days <= lead_days:
        reasons.append(f"Current stock covers about {stock_days:.1f} days, below the {lead_days}-day supplier lead time.")
    elif stock_days <= lead_days + 2:
        reasons.append(f"Only {stock_days:.1f} days of stock remain, close to the {lead_days}-day supplier lead time.")
    else:
        reasons.append(f"Current stock covers about {stock_days:.1f} days.")
    if int(item["criticality"]) >= 4:
        reasons.append("This item has high clinical criticality.")
    if incoming_qty > 0:
        reasons.append(f"{incoming_qty:g} units are listed as incoming" + (f" in {incoming_days} day(s)." if incoming_days is not None else "."))
    else:
        reasons.append("No incoming delivery is recorded.")
    item.update({
        "days_remaining": round(stock_days, 1),
        "risk_score": score,
        "risk_level": level,
        "recommended_order": recommended_order,
        "risk_reasons": reasons,
        "delivery_covers_gap": bool(delivery_covers_gap),
    })
    return item

def read_inventory():
    with connect() as conn:
        return [score_item(r) for r in conn.execute("SELECT * FROM inventory ORDER BY sku").fetchall()]

@app.get("/", response_class=HTMLResponse)
def index():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {"status":"ok","service":"PulseGuard Z","timestamp":datetime.now(timezone.utc).isoformat()}

@app.get("/api/inventory")
def inventory(risk: Optional[str] = None, q: Optional[str] = None):
    items = read_inventory()
    if risk:
        items = [x for x in items if x["risk_level"] == risk.upper()]
    if q:
        term = q.lower()
        items = [x for x in items if term in x["name"].lower() or term in x["category"].lower() or term in x["sku"].lower()]
    return {"items":items,"count":len(items)}

@app.get("/api/summary")
def summary():
    items = read_inventory()
    levels = {k:sum(1 for x in items if x["risk_level"] == k) for k in ["CRITICAL","HIGH","MEDIUM","LOW"]}
    return {
        "total_items":len(items),
        "critical_items":levels["CRITICAL"],
        "high_risk_items":levels["HIGH"],
        "estimated_reorder_units":sum(x["recommended_order"] for x in items),
        "average_risk":round(sum(x["risk_score"] for x in items)/max(1,len(items)),1),
        "risk_breakdown":levels,
        "last_updated":datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/recommendations")
def recommendations():
    items = read_inventory()
    ranked = sorted(items, key=lambda x:(x["risk_score"],x["criticality"]), reverse=True)
    return {"recommendations":[{
        "sku":x["sku"],"name":x["name"],"risk_level":x["risk_level"],
        "risk_score":x["risk_score"],"days_remaining":x["days_remaining"],
        "recommended_order":x["recommended_order"],"reasons":x["risk_reasons"]
    } for x in ranked[:6]]}

class SimulationRequest(BaseModel):
    sku: str
    demand_multiplier: float = Field(default=1.25, ge=0.25, le=5.0)
    stock_delta: float = Field(default=0, ge=-100000, le=100000)

@app.post("/api/simulate")
def simulate(payload: SimulationRequest):
    items = read_inventory()
    item = next((x for x in items if x["sku"] == payload.sku), None)
    if not item:
        raise HTTPException(status_code=404, detail="Unknown SKU")
    baseline = dict(item)
    altered = dict(item)
    altered["daily_use"] = max(0.01, item["daily_use"] * payload.demand_multiplier)
    altered["on_hand"] = max(0, item["on_hand"] + payload.stock_delta)
    result = score_item(altered)
    return {
        "sku":payload.sku,
        "baseline":{"risk_level":baseline["risk_level"],"risk_score":baseline["risk_score"],"days_remaining":baseline["days_remaining"]},
        "scenario":{"risk_level":result["risk_level"],"risk_score":result["risk_score"],"days_remaining":result["days_remaining"]},
        "assumptions":{"demand_multiplier":payload.demand_multiplier,"stock_delta":payload.stock_delta},
        "note":"Scenario only; no inventory records were changed."
    }

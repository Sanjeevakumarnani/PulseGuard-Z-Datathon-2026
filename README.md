# PulseGuard Z — Hospital Supply Shortage Early Warning

**IBM Z Datathon 2026 · Event code: SSF2026**

PulseGuard Z is an explainable early-warning prototype for hospital supply shortages, using stock on hand, daily usage, supplier lead time, incoming deliveries, and criticality. It includes a dashboard, risk-ranked watchlist, replenishment suggestions, and a read-only demand shock simulator.

> **Responsible use:** demo data is synthetic and the risk score is a deterministic heuristic, not a validated clinical or procurement prediction. Human review and validation are required before any real-world use.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

## Test

```bash
python -m unittest discover -s tests -v
```

## Project
- API: FastAPI
- Storage: SQLite
- UI: HTML/CSS/JavaScript
- Container: Docker
- CI: GitHub Actions

See `docs/` for architecture, demo script, and submission text. LinuxONE deployment is not claimed until a real instance and live endpoint have been verified.

**Event code:** `SSF2026`

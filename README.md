# PulseGuard Z — Explainable Hospital Supply Shortage Early Warning

**IBM Z Datathon 2026 · Event code: `SSF2026` · Solo project**

PulseGuard Z is a healthcare-operations prototype that helps teams spot essential hospital supplies at risk of running out. It combines stock on hand, average daily use, supplier lead time, expected incoming deliveries, and item criticality into an explainable risk score, days-of-cover estimate, and suggested replenishment quantity.

> **Responsible-use notice:** This repository uses synthetic demonstration data. Its deterministic score is a prioritization heuristic—not a trained or validated prediction model. Do not use it for real clinical, purchasing, or patient-care decisions without data validation, security controls, operational testing, and qualified human review.

## What it does

- Dashboard KPIs and a risk-ranked inventory watchlist
- Search and filters for critical/high/medium/low risk
- Estimated days of stock remaining vs. supplier lead time
- Explainable score (0–100), reasons, and suggested order quantities
- Read-only demand-shock simulation; saved inventory is not changed
- JSON API and health endpoint
- SQLite demo persistence, Docker packaging, and GitHub Actions test workflow

## Architecture

Browser UI (HTML/CSS/JavaScript) → FastAPI REST API → SQLite inventory. The target deployment is a Linux virtual server on IBM LinuxONE Community Cloud. **Deployment is not claimed until the live instance and endpoint have been verified.**

See [architecture](docs/ARCHITECTURE.md), [demo script](docs/DEMO_SCRIPT.md), [submission copy](docs/SUBMISSION_TEXT.md), and [LinuxONE deployment guide](docs/LINUXONE_DEPLOYMENT.md).

## Run locally

Python 3.11+ recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. Interactive API docs are at http://127.0.0.1:8000/docs. The database is created and seeded on first start. Set `PULSEGUARD_DB` to change the SQLite file path.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The 8 automated tests passed in the local project environment before publication. GitHub Actions is configured to run them on pushes and pull requests; check the Actions tab for the hosted run status.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Service health and timestamp |
| GET | `/api/summary` | Dashboard KPIs and risk breakdown |
| GET | `/api/inventory` | Inventory with calculated risk |
| GET | `/api/inventory?risk=CRITICAL` | Filter by risk |
| GET | `/api/inventory?q=saline` | Search by name, category, or SKU |
| GET | `/api/recommendations` | Highest-priority suggested actions |
| POST | `/api/simulate` | Read-only demand scenario |

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"sku":"MED-001","demand_multiplier":2,"stock_delta":0}'
```

## Risk method and limits

Stock cover is calculated as `on_hand / daily_use`. The scoring heuristic considers stock coverage relative to supplier lead time, configured criticality, and incoming delivery context. Suggested order quantity targets lead time plus a five-day buffer. The score is **not** a probability that a shortage will occur. Validate assumptions against real operational data before any use beyond a demo.

## IBM LinuxONE / event checklist

- [x] Project source published to this public GitHub repository
- [x] Event code `SSF2026` included in project documentation
- [x] Dockerfile, automated tests, and CI workflow included
- [ ] Register/activate LinuxONE Community Cloud account and use event code if requested
- [ ] Create an instance, deploy the application, and verify the live endpoint
- [ ] Capture actual instance/service evidence and record environment details
- [ ] Record the demo and submit the repository/demo on Hack2skill

Official resources:
- [LinuxONE Community Cloud](https://linuxone.cloud.marist.edu/#/login)
- [LinuxONE deployment guide](https://github.com/linuxone-community-cloud/technical-resources/blob/master/faststart/deploy-virtual-server.md)
- [JupyterLab ML setup](https://github.com/linuxone-community-cloud/jupyter-lab-ml)
- [LinuxONE fast start](https://community.ibm.com/zsystems/l1cc/faststart/)
- [Datathon FAQ](https://community.ibm.com/zsystems/datathon/)
- [Hack2skill submission portal](https://hack2skill.com/event/datathon-2026)

## Demo flow (about 3 minutes)

1. Explain why a stock count alone does not show shortage risk.
2. Show the overview metrics and inventory watchlist.
3. Explain one item's stock cover vs. supplier lead time and the score drivers.
4. Run a 2× demand scenario and compare baseline with scenario.
5. If deployed, show the real LinuxONE instance and health endpoint; do not use mock screenshots as deployment evidence.
6. State limitations and next steps: validated demand forecasting, authenticated roles, audit logs, real inventory integrations, and monitoring.

## License

MIT. See [LICENSE](LICENSE).

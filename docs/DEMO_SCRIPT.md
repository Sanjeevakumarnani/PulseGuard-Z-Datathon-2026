# PulseGuard Z — 3-minute demo script

## 0:00–0:25 — Problem
Hospitals can run out of essential supplies even when a shelf appears stocked. The important question is whether current inventory will last through supplier lead time and the next demand cycle.

## 0:25–0:55 — Dashboard
Open the dashboard. Explain the total tracked items, critical/high-risk counts, and that the data is synthetic for the prototype. Point out the ranked inventory watchlist and search/risk filters.

## 0:55–1:35 — Explain a risk
Select a high-risk item. Compare estimated days of stock with supplier lead time. Explain that the score is a transparent heuristic combining stock coverage, lead time, criticality, and incoming delivery data—not a trained model or a validated probability.

## 1:35–2:10 — Demand shock
Open Scenario Lab, choose a supply, and run the 2× demand scenario. Compare baseline and scenario days remaining and risk score. Explain that the simulation is read-only and does not change saved inventory.

## 2:10–2:40 — IBM LinuxONE
Show the actual LinuxONE instance and terminal/service evidence only after deployment. Explain the app runs as a FastAPI service and uses SQLite for this prototype. Do not claim deployment until the live endpoint is verified.

## 2:40–3:00 — Limitations and next steps
The current version uses synthetic data and deterministic rules. Next steps include validated demand forecasting, authenticated roles, audit logs, real inventory integrations, and deployment monitoring. Human review remains necessary for purchasing decisions.

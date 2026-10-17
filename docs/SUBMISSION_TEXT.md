# Hack2skill submission copy

## Project title
PulseGuard Z — Explainable Hospital Supply Shortage Early Warning

## Event code
SSF2026

## Short description
PulseGuard Z is a healthcare operations prototype that helps teams identify essential hospital supplies at risk of running out. It combines stock on hand, daily usage, supplier lead time, incoming deliveries, and clinical criticality into an explainable risk score, estimated days of coverage, and replenishment suggestions. A read-only demand-shock simulator shows how a sudden rise in consumption changes risk. The prototype uses synthetic demo data and is designed for deployment on IBM LinuxONE; the final submission should include verified LinuxONE deployment evidence.

## Problem
Inventory counts alone do not show whether supplies will last until the next delivery. Teams need an interpretable way to prioritize attention before a shortage becomes urgent.

## Solution
PulseGuard Z ranks supplies by shortage risk, explains the drivers behind each alert, and suggests a replenishment quantity based on usage and lead time. Operators can test hypothetical demand spikes without changing saved inventory.

## Responsible-use statement
This is a prototype using synthetic data and a deterministic heuristic. It is not a validated clinical or procurement model. Real-world use would require validated data, security controls, human review, and operational testing.

## Links
- GitHub repository: https://github.com/Sanjeevakumarnani/PulseGuard-Z-Datathon-2026
- Live demo: Add only after deployment and verification
- Demo video: Add after recording

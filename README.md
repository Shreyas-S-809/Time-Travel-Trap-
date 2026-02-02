# Project 6: The Time-Travel Trap ⏳

> **How I built a 99.9% accuracy sales forecasting model that was completely useless — and fixed it.**

## Why this project exists
Most ML models fail in production due to **data leakage**, not bad algorithms.
This project demonstrates:
- Temporal leakage
- Target leakage
- Why offline metrics lie
- How to build leakage-safe pipelines

## Project Structure
- `01_leaky_model.ipynb` → The lie (99.9% accuracy)
- `02_reality_check.ipynb` → The crash
- `03_robust_pipeline.ipynb` → The fix + deployment artifacts

## Key Takeaway
> **Accuracy without causality is a bug, not a feature.**

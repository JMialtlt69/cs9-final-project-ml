# DDoS Traffic Classification Demo

Interactive Streamlit demonstration for the project:

**Leakage-Controlled Supervised Learning for DDoS Traffic Classification: A CICDDoS2019 DrDoS_NetBIOS Study**

## What this app does

The application loads the fitted final Random Forest pipeline exported from the project notebook. It provides:

- one-click BENIGN demonstration
- one-click DrDoS_NetBIOS demonstration
- optional CSV prediction for network-flow records
- predicted class and attack probability

## Model used

- Dataset: CICDDoS2019 — DrDoS_NetBIOS
- Task: BENIGN vs DrDoS_NetBIOS attack
- Model: Random Forest
- Trees: 200
- Random state: 42
- Input predictors: 77
- Correlation-filtered predictors: 52
- Final MI-selected predictors: 30
- Training-only majority-class undersampling

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important scope note

The app is an interactive model demonstration. It is **not** presented as a live network monitor, universal DDoS detector, or independent external validation. The built-in demo records are illustrative application inputs for demonstrating the prediction interface.

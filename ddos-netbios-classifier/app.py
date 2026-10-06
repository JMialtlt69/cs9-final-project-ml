import os
import sys
import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

MODEL_PATH = os.path.join(ROOT, "model", "final_ddos_random_forest_pipeline.joblib")
DEMO_PATH = os.path.join(ROOT, "demo_samples.csv")

st.set_page_config(
    page_title="DDoS Traffic Classification Demo",
    page_icon="🛡️",
    layout="centered",
)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def required_features(model):
    return list(model.named_steps["infinity"].feature_names_in_)


def predict_frame(model, df):
    expected = required_features(model)
    missing = [c for c in expected if c not in df.columns]
    if missing:
        return None, None, missing

    X = df[expected].copy()
    for col in expected:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    pred = model.predict(X)
    prob = model.predict_proba(X)[:, 1]
    return pred, prob, []


def show_result(pred, prob, title=None):
    attack_probability = float(prob)
    is_attack = int(pred) == 1

    st.divider()
    if title:
        st.subheader(title)

    if is_attack:
        st.error("🚨 DrDoS_NetBIOS ATTACK DETECTED")
    else:
        st.success("🟢 BENIGN TRAFFIC")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Predicted class", "DrDoS_NetBIOS" if is_attack else "BENIGN")
    with c2:
        st.metric("Attack probability", f"{attack_probability:.2%}")

    st.progress(attack_probability, text=f"Estimated attack probability: {attack_probability:.2%}")

    st.caption(
        "This is an interactive demonstration of the fitted project model. "
        "It is not a live network monitor or an independent validation study."
    )


st.title("🛡️ DDoS Traffic Classification Demo")
st.write("**CICDDoS2019 — DrDoS_NetBIOS | Final Random Forest**")
st.write(
    "Click a sample test below to run the deployed model, or upload a CSV containing "
    "the 77 predictor columns expected by the final pipeline."
)

try:
    model = load_model()
except Exception as exc:
    st.error("The model could not be loaded.")
    st.exception(exc)
    st.stop()

st.info(
    "**Model:** Random Forest (200 trees)  •  **Final feature set:** 30 features  •  "
    "**Pipeline input:** 77 predictors"
)

try:
    demos = pd.read_csv(DEMO_PATH)
except Exception as exc:
    st.error("Demo sample file could not be loaded.")
    st.exception(exc)
    st.stop()

expected = required_features(model)

st.subheader("One-click demo")
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Test BENIGN Sample", use_container_width=True):
        row = demos[demos["demo_name"] == "BENIGN demo"].drop(columns=["demo_name"])
        pred, prob, missing = predict_frame(model, row)
        if missing:
            st.error(f"Demo sample is missing {len(missing)} required columns.")
        else:
            show_result(pred[0], prob[0], "BENIGN sample result")

with col2:
    if st.button("▶ Test DrDoS_NetBIOS Sample", use_container_width=True):
        row = demos[demos["demo_name"] == "DrDoS_NetBIOS demo"].drop(columns=["demo_name"])
        pred, prob, missing = predict_frame(model, row)
        if missing:
            st.error(f"Demo sample is missing {len(missing)} required columns.")
        else:
            show_result(pred[0], prob[0], "DrDoS_NetBIOS sample result")

st.subheader("Custom CSV prediction")
uploaded = st.file_uploader("Upload a CSV network-flow record", type=["csv"])

if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        st.write(f"Loaded **{len(uploaded_df):,}** row(s).")

        pred, prob, missing = predict_frame(model, uploaded_df)
        if missing:
            st.error("The uploaded CSV is missing required predictor columns.")
            with st.expander("Show missing columns"):
                st.code("\n".join(missing))
        else:
            results = uploaded_df.copy()
            results["Predicted Class"] = np.where(pred == 1, "DrDoS_NetBIOS", "BENIGN")
            results["Attack Probability"] = prob
            st.dataframe(
                results[["Predicted Class", "Attack Probability"]],
                use_container_width=True,
            )
    except Exception as exc:
        st.error("The uploaded CSV could not be processed.")
        st.exception(exc)

with st.expander("What the application is doing"):
    st.markdown(
        """
        1. Loads the fitted Random Forest pipeline exported from the final notebook.
        2. Accepts the same 77 predictor columns used by the final pipeline.
        3. Applies the fitted preprocessing and 30-feature selection inside the saved pipeline.
        4. Returns a BENIGN or DrDoS_NetBIOS prediction and the model's attack probability.

        **Project limitation:** this demonstration does not claim live packet capture,
        universal DDoS detection, or independent external validation.
        """
    )

with st.expander("Required CSV columns"):
    st.code("\n".join(expected))

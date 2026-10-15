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
    "Enter a flow manually, click a one-click sample, or upload a CSV containing "
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

# ---------------------------------------------------------------------------
# Manual input helpers
# ---------------------------------------------------------------------------
def selected_features(model):
    """The 30 features that actually reach the Random Forest (after correlation + MI selection)."""
    corr = model.named_steps["correlation"].get_feature_names_out().tolist()
    keep = model.named_steps["mi"].get_support()
    return [f for f, k in zip(corr, keep) if k]


FEATURE_GROUPS = {
    "⏱ Flow timing & rate": [
        "Flow Duration", "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean", "Flow IAT Min",
        "Bwd Packets/s",
    ],
    "📦 Packet counts & sizes": [
        "Total Fwd Packets", "Total Backward Packets", "Total Length of Fwd Packets",
        "Total Length of Bwd Packets", "Fwd Packet Length Max", "Fwd Packet Length Min",
        "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
        "Max Packet Length", "Packet Length Std", "Packet Length Variance",
    ],
    "↩ Backward inter-arrival times": [
        "Bwd IAT Total", "Bwd IAT Mean", "Bwd IAT Max", "Bwd IAT Min",
    ],
    "🧾 Headers, flags & window": [
        "Fwd Header Length", "Bwd Header Length", "URG Flag Count", "Down/Up Ratio",
        "Init_Win_bytes_forward", "Init_Win_bytes_backward", "act_data_pkt_fwd",
        "min_seg_size_forward",
    ],
}

# Typical (median) flows taken from the authentic CICDDoS2019 holdout sample; used as presets.
FALLBACK_PRESETS = {}


@st.cache_data
def load_presets(features):
    path = os.path.join(ROOT, "sample_csvs", "authentic_cicddos2019_sample.csv")
    presets = {}
    try:
        df = pd.read_csv(path)
        for label, name in (("BENIGN", "Typical BENIGN flow"), ("DrDoS_NetBIOS", "Typical DrDoS_NetBIOS flow")):
            sub = df[df["True Label"] == label][list(features)]
            presets[name] = {f: float(sub[f].median()) for f in features}
    except Exception:
        pass
    presets["All zeros (blank form)"] = {f: 0.0 for f in features}
    return presets


def apply_preset(features, presets):
    chosen = st.session_state.get("preset_choice")
    if chosen in presets:
        for f in features:
            st.session_state[f"in_{f}"] = presets[chosen][f]


def build_input_row(model, values):
    """77-column frame the pipeline expects. The 47 columns the model discards are filled with 0."""
    row = {c: 0.0 for c in required_features(model)}
    row.update(values)
    return pd.DataFrame([row])


tab_manual, tab_demo, tab_csv = st.tabs(["✍️ Manual input", "▶ One-click demo", "📄 Upload CSV"])

with tab_manual:
    feats = tuple(selected_features(model))
    presets = load_presets(feats)
    preset_names = list(presets.keys())

    st.subheader("Manual flow input")
    st.write(
        "Enter the network-flow values yourself and the deployed Random Forest will classify the flow as "
        "**BENIGN** or **DrDoS_NetBIOS**. The form shows the **30 features the model actually uses**."
    )

    if "preset_choice" not in st.session_state:
        st.session_state["preset_choice"] = preset_names[0]
        for f in feats:
            st.session_state[f"in_{f}"] = presets[preset_names[0]][f]

    st.selectbox(
        "Start from a preset (then edit any value)",
        preset_names,
        key="preset_choice",
        on_change=apply_preset,
        args=(feats, presets),
    )

    grouped = {g: [f for f in fl if f in feats] for g, fl in FEATURE_GROUPS.items()}
    leftover = [f for f in feats if all(f not in fl for fl in grouped.values())]
    if leftover:
        grouped["Other"] = leftover

    with st.form("manual_form"):
        for group, flist in grouped.items():
            if not flist:
                continue
            with st.expander(group, expanded=True):
                cols = st.columns(2)
                for i, f in enumerate(flist):
                    cols[i % 2].number_input(f, key=f"in_{f}", format="%.6g", step=1.0)
        submitted = st.form_submit_button("🔍 Classify this flow", width="stretch", type="primary")

    if submitted:
        values = {f: float(st.session_state[f"in_{f}"]) for f in feats}
        if all(v == 0 for v in values.values()):
            st.warning("Every value is 0, which is not a realistic flow. Pick a preset or enter real values.")
        frame = build_input_row(model, values)
        pred, prob, missing = predict_frame(model, frame)
        if missing:
            st.error(f"Missing {len(missing)} required columns.")
        else:
            show_result(pred[0], prob[0], "Manual input result")
            with st.expander("Values sent to the model"):
                st.dataframe(pd.DataFrame({"Feature": list(values), "Value": list(values.values())}),
                             width="stretch", hide_index=True)

    st.caption(
        "The model is binary (BENIGN vs. DrDoS_NetBIOS), so these are the only two classes it can return. "
        "The other 47 CICFlowMeter columns are removed by the pipeline's correlation filter and "
        "mutual-information selection, so they are set to 0 behind the scenes and do not affect the result. "
        "Raw CICFlowMeter units apply (durations and inter-arrival times in microseconds)."
    )

with tab_demo:
    st.subheader("One-click demo")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Test BENIGN Sample", width="stretch"):
            row = demos[demos["demo_name"] == "BENIGN demo"].drop(columns=["demo_name"])
            pred, prob, missing = predict_frame(model, row)
            if missing:
                st.error(f"Demo sample is missing {len(missing)} required columns.")
            else:
                show_result(pred[0], prob[0], "BENIGN sample result")

    with col2:
        if st.button("▶ Test DrDoS_NetBIOS Sample", width="stretch"):
            row = demos[demos["demo_name"] == "DrDoS_NetBIOS demo"].drop(columns=["demo_name"])
            pred, prob, missing = predict_frame(model, row)
            if missing:
                st.error(f"Demo sample is missing {len(missing)} required columns.")
            else:
                show_result(pred[0], prob[0], "DrDoS_NetBIOS sample result")


with tab_csv:
    st.subheader("Custom CSV prediction")
    uploaded = st.file_uploader("Upload a CSV network-flow record", type=["csv"])

    SAMPLE_DIR = os.path.join(ROOT, "sample_csvs")
    with st.expander("Download sample CSVs to try"):
        st.caption(
            "Authentic = real CICDDoS2019 DrDoS_NetBIOS holdout flows. Synthetic = bootstrap + jitter "
            "stress-test data generated from the training set. Both include a 'True Label' column."
        )
        for fname, label in [
            ("authentic_cicddos2019_sample.csv", "Authentic CICDDoS2019 sample (200 rows)"),
            ("synthetic_stress_sample.csv", "Synthetic stress-test sample (200 rows)"),
        ]:
            fpath = os.path.join(SAMPLE_DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, "rb") as fh:
                    st.download_button(f"⬇ {label}", fh.read(), file_name=fname, mime="text/csv")

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
                label_col = next((c for c in ("True Label", "Label") if c in uploaded_df.columns), None)
                if label_col is not None:
                    truth = uploaded_df[label_col].astype(str).str.strip()
                    truth = truth.replace({"0": "BENIGN", "1": "DrDoS_NetBIOS"})
                    results["Correct"] = np.where(results["Predicted Class"] == truth, "✔", "✘")
                    acc = (results["Correct"] == "✔").mean()
                    m1, m2 = st.columns(2)
                    m1.metric("Accuracy vs. true labels", f"{acc:.2%}")
                    m2.metric("Misclassified rows", int((results["Correct"] == "✘").sum()))
                    st.write("**Confusion matrix** (rows = actual, columns = predicted)")
                    st.dataframe(
                        pd.crosstab(truth.rename("Actual"), results["Predicted Class"].rename("Predicted")),
                        width="stretch",
                    )
                    show_cols = ["Predicted Class", "Attack Probability", "Correct"]
                else:
                    show_cols = ["Predicted Class", "Attack Probability"]
                st.dataframe(results[show_cols], width="stretch")
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

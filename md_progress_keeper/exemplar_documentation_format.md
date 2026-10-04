# Reference: Exemplar Final Project Documentation Format
*(Based on "Predicting High-Performing Employees for Task Allocation Using Machine Learning" — Mizal Analytics, by Kaye Ashley B. Mizal, University of Mindanao)*

This is a structural reference only — use it to shape your own DDoS classification write-up, not to copy content from. It's an IEEE-conference-paper-style format (two-column layout, 8 pages), distinct from the CCE105 milestone template you've been using, so check with your instructor which one this milestone actually requires.

---

## Overall Shape

Single flowing paper with numbered top-level sections (1–5) and numbered subsections (x.x), plus header block, abstract, keywords, figures/tables embedded inline, and references at the end.

**Header block:**
- Title (project/system name + one-line description of what it predicts/does)
- Author name, affiliation (university, city, country), institutional email

**Abstract** (~150–200 words, one paragraph, no heading subdivisions):
- What the system does and why (1–2 sentences)
- Dataset used + size
- Models used + which was chosen and why
- Key features evaluated
- Headline result (one accuracy/metric number)
- One sentence on the strongest predictive finding
- One sentence framing the system as decision-support, not a replacement for human judgment

**Keywords** — 5–7 terms (technique names, domain terms, business terms), em-dash separated.

---

## 1. Introduction

**1.1 Business/Problem Description** — Frames the real-world problem first (not the ML problem). States why the current manual/ad-hoc approach is inconsistent or unreliable, who is affected, and what downside motivates automating it. Cites 1–2 authoritative frameworks/standards relevant to the domain (here: NIST AI RMF, OECD AI Principles) to ground the "why this matters" in recognized guidance. Ends by stating the system is decision-support, not a replacement for human judgment — an explicit scope-limiting sentence.

**1.2 Objectives** — One general objective sentence, then a bulleted list of 3 specific objectives: (1) build the model, (2) compare at least two model types, (3) deliver something usable/explainable for the end stakeholder — not just "get good accuracy."

---

## 2. Methodology

**2.1 Dataset Overview** — Source (name, platform, author/publisher, citation), exact record count, which specific file was used, and an explicit note on any modification to the original dataset (e.g., added synthetic rows) plus why. States why the dataset fits the problem, and candidly notes a limitation of using a synthetic/educational dataset (so the result is framed as a prototype pending real-world validation).
- Includes a **feature table**: Feature Name | Type (Numerical/Categorical/Target/etc.) | Description/Relevance — one row per raw column.
- Includes a labeled **Figure** (data lineage / sample records) with a caption and a short paragraph explaining what the figure shows and why it matters.

**2.2 Data Analysis** — States row/column counts, missing-value count, duplicate-ID count. Flags any imbalance in a candidate target field and explains why it was rejected as the target.
- Includes a **Data Quality table**: Quality Area | Finding | Impact on Modeling (missing values, duplicates, outliers, class distribution, feature scales) — this is the "what we checked and what we did about it" table.
- Includes figures for target-variable distribution and feature-scale/outlier comparison, each with a caption + interpretive paragraph.

**2.3 Data Preparation and Feature Engineering** — Narrative list of cleaning steps (dedup, numeric conversion, missing-value handling, outlier clipping, composite-score engineering). States which raw features were kept as predictors vs. excluded (and why — e.g., excluded to avoid rewarding the wrong behavior) vs. retained only as metadata.
- Includes a **Feature Weight table**: Feature | Weight (%) | Business Meaning — used when the target itself is an engineered composite score, showing exactly how the score formula was built.
- States the composite-score formula in prose (coefficients spelled out) and the percentile cutoff used to binarize it, with the resulting class counts.
- Includes a figure showing the composite-score distribution and threshold.

**2.4 Predictive Modeling Approaches** — Two labeled subsections:
- **2.4.1 Human-Implemented Model** (the simpler/baseline algorithm) — what it is, one in-text citation for the algorithm, why chosen, its main limitation stated honestly.
- **2.4.2 AI-Recommended Predictive Model** (the stronger/final algorithm) — what it is, one in-text citation, why it suits this specific problem's structure (e.g., multiple interacting factors).

**2.5 Model Comparison and Initial Evaluation** — States exactly which metrics were used (accuracy, weighted precision/recall/F1, cross-validation accuracy, confusion matrix, "business suitability"). Frames the comparison as weighing technical performance against the business need for explainability, not accuracy alone.
- Includes a **comparison table**: Metric | Model A (Baseline) | Model B (Final) — same metric set, side by side, rows for overall + per-class + CV.
- Includes a figure (bar chart) visualizing baseline vs. final model, with caption + one interpretive paragraph.

**2.6 Model Refinement and Performance Improvement** — Explains what was changed to reduce overfitting/improve generalization (e.g., recalibrating the target, adding cleaning steps, tuning hyperparameters).
- Includes a **hyperparameter table**: Parameter | Final Value | Purpose (plain-language reason for each setting, not just the value).
- States the final headline metric (here: out-of-bag accuracy) and explains *why* that evaluation method is valid for the chosen model (e.g., OOB validity for Random Forest's bootstrap sampling).
- Includes a **Final Result summary table**: Dataset size, class counts, cutoff score, headline accuracy — a compact "final numbers" box.
- Includes a confusion-matrix table (Actual × Predicted) and a figure/caption interpreting false positive/false negative counts relative to dataset size.

---

## 3. Results

**3.1 Final Evaluation Metrics** — Restates the headline metric and the evaluation method's validity in 1–2 sentences (no new numbers beyond what 2.6 already established — this section is about stating results plainly, not re-deriving them).

**3.2 Feature Importance** — One framing sentence tying feature importance to explainable-AI principles (with citation).
- Includes a **ranked feature importance table**: Rank | Feature | Importance (numeric) | Business Interpretation (plain-language meaning of why this feature matters) — every row gets a business-meaning sentence, not just a number.
- Includes the corresponding figure (bar chart) with caption.

**3.3 Model Findings and Visualizations** — A short synthesis paragraph (3 numbered "findings") tying the target design, the model comparison, and the feature importance together into one coherent story the reader can walk away with.

---

## 4. Discussion

**4.1 Model Performance** — Interprets the headline numbers (OOB + test accuracy together) as evidence the model learned a real relationship, referencing the confusion matrix's balance across classes.

**4.2 Model Suitability** — Why the model fits the deployment context (practicality, explainability, integration potential), paired with an explicit statement that it supports — not replaces — human decision-making.

**4.3 Comparison of Models** — A head-to-head paragraph restating each model's core trade-off (interpretability vs. accuracy/stability) and justifying the final choice.

**4.4 Business Interpretation of Important Features** — Walks through the top features again, this time explaining *why* each ranks where it does in terms a non-technical stakeholder would understand (including reconciling any mismatch between a feature's assigned "weight" in the composite score vs. its actual learned importance — an honest, non-hand-wavy point).

**4.5 Business Insights, Risks, and Deployment Considerations** — Two parts: (a) the positive insight a manager/stakeholder can act on, (b) risks and caveats — dataset being synthetic/engineered, need for real-world validation, bias monitoring, human review for high-impact decisions, explicit exclusion of ethically-risky signals (e.g., not rewarding overwork).

---

## 5. Conclusion and Recommendations

One paragraph restating: what the project delivered, which model was retained as baseline vs. final and why, the headline metric, and a forward-looking paragraph of concrete next steps (collect real-world data, retrain periodically, keep human review, keep excluding ethically-risky features).

---

## References

Numbered IEEE style, in citation order (not alphabetical), each with DOI/URL where available. Mix of: standards/framework documents, the dataset's own citation, and the 1–2 foundational algorithm papers (Quinlan for Decision Trees, Breiman for Random Forest) plus one explainability-AI citation.

---

## Conventions Worth Copying Into Your Own Draft

1. **Every table has a business-meaning column**, not just numbers — "Impact on Modeling," "Business Meaning," "Business Interpretation," "Purpose." Numbers alone are never left to speak for themselves.
2. **Every figure has a caption AND a follow-up paragraph** that states what to notice in it — never just "Figure X shows Y," always "...which means Z."
3. **Baseline vs. final model framing is maintained throughout**, not just in a results table — introduced in 2.4, compared in 2.5, revisited in 3.3, 4.1, and 4.3.
4. **Limitations are disclosed proactively and specifically** (synthetic data, engineered target, excluded features) rather than hedged generically — and tied to concrete next steps in the conclusion.
5. **A business/ethical boundary is stated explicitly at least twice** (abstract + discussion): the system assists, it doesn't replace human judgment; it deliberately avoids rewarding a undesirable proxy signal (overwork).
6. **Hyperparameters are justified in plain language**, each with a one-line "why this setting" — not left as a bare config dump.

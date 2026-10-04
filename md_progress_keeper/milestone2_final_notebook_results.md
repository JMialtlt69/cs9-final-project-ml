# Milestone 2 — Final Notebook Results (Verified, Complete Run)

**Source:** `Copy_of_DrDoS_NetBIOS_Leakage_Controlled_Final.ipynb` (54 cells, fully executed)
**Purpose of this file:** authoritative reference to fill every `BLOCKER` placeholder in the Milestone 2 PDF draft. All numbers below are read directly from actual cell outputs — nothing here is estimated or invented.

---

## 0. Configuration (as run)

```
RANDOM_STATE = 42
TEST_SIZE = 0.20
CORRELATION_THRESHOLD = 0.95
CV_FOLDS = 5
RF_TREES = 200 (final model) / 200 (baseline — same n_estimators used throughout)
Sampling strategy = 'majority' (dynamic RandomUnderSampler — matches majority class
                     down to minority class count, NOT a fixed 1,302/1,302 as earlier drafts assumed)
DATA_PATH = /content/drive/MyDrive/CS9L_FinalProject_Files/CSV-01-12/01-12/DrDoS_NetBIOS.csv
```

Note: earlier drafts referenced a fixed "1,302 benign / 1,302 attack" balanced training sample. The actual notebook uses `RandomUnderSampler(sampling_strategy='majority')` inside the pipeline, which dynamically undersamples the attack class to match whatever the benign class count is in each fit (train fold or full training set) — not a hardcoded number. The 1,302 figure that appears later is the *actual* training-set benign count after the real split, not a configured target.

---

## 1. Raw Dataset Audit

- **Raw shape:** 4,094,986 rows × 88 columns
- **Raw label counts:** DrDoS_NetBIOS (attack) = 4,093,279 | BENIGN = 1,707

## 2. Cleaning Pipeline (global, before train/test split)

**Columns dropped (10 total):**
- Identifiers: `Unnamed: 0`, `Flow ID`, `Source IP`, `Destination IP`, `Timestamp`, `SimillarHTTP`
- Leakage-prone: `Source Port`, `Destination Port`, `Protocol`, `Inbound`

Shape after column drop: **4,094,986 × 78**

**Infinity handling:**
- Columns containing Infinity: `Flow Bytes/s`, `Flow Packets/s`
- Infinity values replaced with NaN

**Missing values:**
- Rows containing NaN (post-Infinity-replacement): **129,853** — all removed
- Shape after NaN drop: **3,965,133 × 78**

**Duplicates:**
- Duplicates removed: **3,945,620**
- Shape after dedup: **19,513 × 78**

**Final cleaned feature matrix:** X = 19,513 × 77 (Label dropped out as target)
**Final class counts:** Benign (0) = 1,627 | Attack (1) = 17,886

| Class | Count | Proportion |
|---|---|---|
| Attack | 17,886 | 91.66% |
| Benign | 1,627 | 8.34% |
| **Total** | **19,513** | **100%** |

---

## 3. Train/Test Split (stratified, 80/20, random_state=42)

| Partition | Total | Benign | Attack |
|---|---|---|---|
| Train | 15,610 | 1,302 | 14,308 |
| Test (holdout, untouched) | 3,903 | 325 | 3,578 |

---

## 4. Leakage-Controlled Pipeline Components

Each model is a single `imblearn` Pipeline, fitted on training data only:

```
InfinityMaxImputer()        — fits per-column max finite value on TRAIN only, imputes Infinity with it
CorrelationFilter(0.95)     — fits on TRAIN only, drops features with pairwise |corr| > 0.95
RandomUnderSampler('majority', random_state=42)  — undersamples attack class to match benign count, TRAIN only
[SelectKBest(mutual_info_classif, k=K)]           — MI feature selection, TRAIN only (final model only)
Classifier (DecisionTreeClassifier or RandomForestClassifier)
```

This fold-specific/train-only fitting is what makes the pipeline "leakage-controlled" — the test set never influences imputation values, correlation thresholds, undersampling, or feature selection.

---

## 5. Baseline Models (77 features, before MI selection)

### 5.1 Decision Tree Baseline (max_depth=3)

```
              precision    recall  f1-score   support
Benign          0.8346     0.9938    0.9073      325
Attack          0.9994     0.9821    0.9907     3578
accuracy                              0.9831     3903
```

**Confusion Matrix:** TN=323, FP=2, FN=64, TP=3514
**ROC-AUC:** 0.9911 | **Average Precision:** 0.9985

### 5.2 Random Forest Baseline (n_estimators=200, all 77 features, no MI selection)

```
              precision    recall  f1-score   support
Benign          0.9393     1.0000    0.9687      325
Attack          1.0000     0.9941    0.9971     3578
accuracy                              0.9946     3903
```

**Confusion Matrix:** TN=325, FP=0, FN=21, TP=3557
**ROC-AUC:** 0.9999 | **Average Precision:** 1.0000

### 5.3 Baseline RF — 5-Fold Cross-Validation (training set, 77 features)

| Metric | Mean | Std |
|---|---|---|
| Accuracy | 0.993017 | 0.002476 |
| Precision | 0.999648 | 0.000315 |
| Recall | 0.992732 | 0.002737 |
| F1 | 0.996176 | 0.001360 |
| ROC-AUC | 0.999482 | 0.000811 |
| Average Precision | 0.999914 | 0.000150 |

---

## 6. Mutual-Information Feature Selection Experiment

5-fold CV across candidate feature counts (10, 20, 30, 40, 52), each with a fresh pipeline (Infinity → Correlation → Undersample → SelectKBest(MI, k) → RF):

| Feature Count | Accuracy | Precision | Recall | F1 | F1 Std | ROC-AUC | AP | AP Std |
|---|---|---|---|---|---|---|---|---|
| 10 | 0.985010 | 0.999291 | 0.984345 | 0.991760 | 0.001001 | 0.998380 | 0.999778 | 0.000133 |
| 20 | 0.991224 | 0.999719 | 0.990705 | 0.995189 | 0.001462 | 0.999433 | 0.999910 | 0.000150 |
| **30** | **0.993722** | **0.999649** | **0.993500** | **0.996564** | **0.001016** | **0.999501** | **0.999916** | **0.000150** |
| 40 | 0.992441 | 0.999648 | 0.992103 | 0.995858 | 0.001815 | 0.999486 | 0.999915 | 0.000149 |
| 52 | 0.993017 | 0.999648 | 0.992732 | 0.996176 | 0.001360 | 0.999482 | 0.999914 | 0.000150 |

**Selection rule:** highest Attack F1 among candidates within one standard error of the best, then tie-broken by recall → AP → stability (lower F1 std) → fewer features.

- Best F1 = 0.996564 (K=30); SE = 0.000454
- Eligible within 1-SE band: K=30 (F1=0.996564) and K=52 (F1=0.996176)
- **Winner: FINAL_K = 30** (higher recall, higher AP, lower F1 std, and fewer features than K=52)

### Feature-Space Reduction

| Stage | Feature Count |
|---|---|
| Initial predictive (post-cleaning) | 77 |
| After correlation filtering (>0.95 threshold) | 52 |
| Final MI-selected | 30 |

---

## 7. Final 30 Selected Features (exact, in selection order)

```
01. Flow Duration              11. Flow Bytes/s           21. Bwd Packets/s
02. Total Fwd Packets          12. Flow Packets/s         22. Max Packet Length
03. Total Backward Packets     13. Flow IAT Mean          23. Packet Length Std
04. Total Length of Fwd Packets 14. Flow IAT Min          24. Packet Length Variance
05. Total Length of Bwd Packets 15. Bwd IAT Total         25. URG Flag Count
06. Fwd Packet Length Max      16. Bwd IAT Mean           26. Down/Up Ratio
07. Fwd Packet Length Min      17. Bwd IAT Max            27. Init_Win_bytes_forward
08. Bwd Packet Length Max      18. Bwd IAT Min            28. Init_Win_bytes_backward
09. Bwd Packet Length Min      19. Fwd Header Length      29. act_data_pkt_fwd
10. Bwd Packet Length Mean     20. Bwd Header Length      30. min_seg_size_forward
```

None of the four previously-flagged leakage columns (Source Port, Destination Port, Protocol, Inbound) appear — confirming they were excluded at the global cleaning stage, before feature selection ever ran.

---

## 8. FINAL MODEL — Random Forest, 30 Features (the model to report as primary result)

### 8.1 Real Holdout Performance (untouched 3,903-row test set)

```
              precision    recall  f1-score   support
Benign          0.9448     1.0000    0.9716      325
Attack          1.0000     0.9947    0.9973     3578
accuracy                              0.9951     3903
macro avg       0.9724     0.9973    0.9845     3903
weighted avg    0.9954     0.9951    0.9952     3903
```

**Confusion Matrix (Final Random Forest — Real Holdout):**

| | Predicted Benign | Predicted Attack |
|---|---|---|
| **Actual Benign** | 325 (TN) | 0 (FP) |
| **Actual Attack** | 19 (FN) | 3,559 (TP) |

**ROC-AUC:** 0.9999 | **Average Precision (PR-AUC):** 1.0000

### 8.2 Final Model — 5-Fold Cross-Validation (30-feature config, training set)

| Metric | Mean | Std | Fold 1 | Fold 2 | Fold 3 | Fold 4 | Fold 5 |
|---|---|---|---|---|---|---|---|
| Accuracy | 0.993722 | 0.001852 | 0.991992 | 0.992633 | 0.992633 | 0.994234 | 0.997117 |
| Precision | 0.999649 | 0.000221 | 0.999648 | 1.000000 | 0.999648 | 0.999649 | 0.999300 |
| Recall | 0.993500 | 0.002194 | 0.991614 | 0.991964 | 0.992313 | 0.994058 | 0.997553 |
| F1 | 0.996564 | 0.001016 | 0.995615 | 0.995966 | 0.995967 | 0.996845 | 0.998426 |
| ROC-AUC | 0.999501 | 0.000813 | 0.999938 | 0.999954 | 0.999857 | 0.999878 | 0.997876 |
| AP | 0.999916 | 0.000150 | 0.999994 | 0.999996 | 0.999987 | 0.999988 | 0.999616 |

This is the figure for **Section 13 (Five-Fold Cross-Validation Robustness)** in your PDF draft — low fold-to-fold variance (all stds ≤0.0022) supports stability of the 30-feature configuration.

### 8.3 Feature Importance — Final Random Forest (Gini importance, all 30 features)

| Feature | Importance |
|---|---|
| Fwd Packet Length Min | 0.1882 |
| Total Length of Fwd Packets | 0.1365 |
| Fwd Packet Length Max | 0.0994 |
| Total Backward Packets | 0.0708 |
| Max Packet Length | 0.0621 |
| Bwd Packets/s | 0.0559 |
| Bwd IAT Max | 0.0510 |
| Flow Bytes/s | 0.0453 |
| Bwd Header Length | 0.0440 |
| Init_Win_bytes_forward | 0.0326 |
| Packet Length Variance | 0.0272 |
| Bwd IAT Mean | 0.0248 |
| Bwd IAT Total | 0.0235 |
| Packet Length Std | 0.0203 |
| URG Flag Count | 0.0146 |
| Flow Duration | 0.0137 |
| act_data_pkt_fwd | 0.0128 |
| Flow Packets/s | 0.0125 |
| Bwd IAT Min | 0.0089 |
| Init_Win_bytes_backward | 0.0085 |
| Flow IAT Mean | 0.0084 |
| Fwd Header Length | 0.0075 |
| Flow IAT Min | 0.0060 |
| min_seg_size_forward | 0.0055 |
| Down/Up Ratio | 0.0049 |
| Bwd Packet Length Mean | 0.0049 |
| Total Fwd Packets | 0.0047 |
| Bwd Packet Length Max | 0.0032 |
| Total Length of Bwd Packets | 0.0022 |
| Bwd Packet Length Min | 0.0001 |

---

## 9. Synthetic Stress Test

**Generation procedure** (fills the "do not invent a stress-test score" blocker from the PDF):
- 1,000 synthetic Benign + 1,000 synthetic Attack samples (2,000 total)
- Built by bootstrapping real rows from the **training partition only** (never test data) per class
- Each bootstrapped row perturbed with Gaussian jitter: `noise ~ N(0, IQR × 0.05)` per feature (falls back to std if IQR=0)
- Perturbed values clipped to the [1st, 99th] percentile range observed in training data
- `random_state=142` (reproducible)
- Evaluated using the **already-fitted final 30-feature pipeline** (no retraining)

**Results:**

```
              precision    recall  f1-score   support
Benign          0.9477     0.9970    0.9717     1000
Attack          0.9968     0.9450    0.9702     1000
accuracy                              0.9710     2000
```

**Confusion Matrix (Synthetic Stress Test):**

| | Predicted Benign | Predicted Attack |
|---|---|---|
| **Actual Benign** | 997 (TN) | 3 (FP) |
| **Actual Attack** | 55 (FN) | 945 (TP) |

**ROC-AUC:** 0.9983 | **Average Precision:** 0.9983

### Real Holdout vs. Synthetic Stress — Comparison

| Metric | Real Holdout | Synthetic Stress |
|---|---|---|
| Accuracy | 0.9951 | 0.9710 |
| Benign F1 | 0.9716 | 0.9717 |
| Attack Precision | 1.0000 | 0.9968 |
| Attack Recall | 0.9947 | 0.9450 |
| Attack F1 | 0.9973 | 0.9702 |
| ROC-AUC | 0.9999 | 0.9983 |
| Average Precision | 1.0000 | 0.9983 |

Interpretation: performance degrades modestly (not catastrophically) under jittered/perturbed synthetic traffic — attack recall drops the most (0.9947 → 0.9450), suggesting the model is somewhat sensitive to small distributional shifts away from the exact training distribution, which is an honest robustness finding rather than a red flag.

---

## 10. Decision Tree vs. Final Random Forest — Apple-to-Apple Comparison

Both evaluated on the same real holdout set (the Decision Tree baseline uses 77 features / no MI selection, since the Decision Tree was never re-run through the 30-feature MI pipeline — see caveat below):

| Metric | Decision Tree (baseline, 77 features) | Final Random Forest (30 features) |
|---|---|---|
| Accuracy | 0.9831 | 0.9951 |
| Attack Precision | 0.9994 | 1.0000 |
| Attack Recall | 0.9821 | 0.9947 |
| Attack F1 | 0.9907 | 0.9973 |
| ROC-AUC | 0.9911 | 0.9999 |
| Average Precision | 0.9985 | 1.0000 |

**Caveat carried over honestly:** the Decision Tree was evaluated on the original 77-feature set, not re-run through the final 30-feature MI-selected pipeline. The comparison is informative (both are leakage-controlled, both use the same train/test split) but not a perfectly controlled ablation. If your instructor wants a strict apples-to-apples test, the Decision Tree would need to be retrained inside `make_rf`-equivalent with `k=30`.

---

## 11. Error Analysis (False Positive / False Negative Rates)

| Model | TP | TN | FP | FN | FPR | FNR |
|---|---|---|---|---|---|---|
| Decision Tree Baseline | 3514 | 323 | 2 | 64 | 0.615385% | 1.7887% |
| Final Random Forest (30 feat.) | 3559 | 325 | 0 | 19 | 0.000000% | 0.531023% |

- **FPR** = FP / (TN + FP) — rate of benign traffic wrongly flagged as attack
- **FNR** = FN / (TP + FN) — rate of attack traffic wrongly passed as benign (the more operationally dangerous error in DDoS detection)

The final Random Forest eliminates false positives entirely on this holdout set and roughly a third the Decision Tree's false-negative rate.

---

## 12. Limitations (as stated in notebook)

- The experiment uses a single CICDDoS2019 DrDoS_NetBIOS traffic scenario and should not be interpreted as universal network-intrusion performance.
- The cleaned dataset remains attack-heavy, so accuracy alone is not sufficient for interpretation.
- Under-sampling discards part of the majority class during training.
- The synthetic stress-test experiment is training-derived and is not external, real-world validation.
- Colab resource limits motivate single-process cross-validation.
- Independent traffic from another environment would be needed to assess stronger real-world generalization.

## 13. Conclusion (as stated in notebook)

The final model is selected using training-only cross-validation, then retrained on the complete training partition before the untouched real holdout is evaluated. The synthetic experiment provides a controlled stress test, while the real holdout remains the primary efficacy result. The saved model, feature list, selection results, evaluation results, and figures provide the artifacts required for the project documentation.

---

## 14. Mapping to the PDF Draft's BLOCKERs

| PDF Section | Blocker | Resolved value (this document) |
|---|---|---|
| §10.1 Holdout Performance table | "Historical Decision Tree result" row | Already correct in PDF (98.31%/99.94%/98.21%) — no change needed |
| §10.1 confusion matrix blocker | Insert final RF holdout CM | §8.1 above — [[325,0],[19,3559]] (PDF's own inline figure already had this right) |
| §10.3 Synthetic stress blocker | Generation procedure, seed, sample size, metrics | §9 above — full procedure, seed=142, n=1000/class, all metrics |
| §11 Decision Tree vs RF table | Precision/Recall/F1/ROC-AUC "Blocker" cells | §10 above — full table, both models |
| §14 Feature importance blocker | Final top-feature ranking, 30-feature RF | §8.3 above — full 30-feature list |
| §Appendix C | Decision Tree & RF holdout confusion matrices | §5.1 and §8.1 above — both matrices, exact counts |
| §Appendix D | Every "BLOCKER" cell in Final Performance Summary | §8.1 above — Accuracy 99.51%, Precision 100%, Recall 99.47%, F1 99.73%, ROC-AUC 99.99%, AP 100% |
| §13 CV blocker | Mean/std per metric, final 30-feature pipeline | §8.2 above — full table with per-fold breakdown |

**Remaining true gap (not resolved by this notebook):** the Decision Tree was never re-run through the final 30-feature MI pipeline, so a strictly-matched baseline-vs-final comparison (§11, §17.3 in the PDF) is not available — only the baseline-vs-final comparison across *different* feature counts (77 vs. 30), which is what's reported above. Flag this to your instructor as a known, disclosed limitation rather than silently presenting it as a controlled ablation.

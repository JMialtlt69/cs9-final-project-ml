# Classifying DDoS Traffic Patterns Through Supervised Learning

**A Project Documentation**
Presented to The University of Mindanao, College of Computing Education
In Partial Fulfillment of the Requirements in CCE105
1st Semester, 1st Term S.Y. 2026-2027
September 2026

---

## 3. Data Quality Analysis

### 3.1. Removal of Identifier and Testbed-Artifact Columns

Ten columns were predetermined for removal in the original experimental design: `Unnamed: 0`, `Flow ID`, `Source IP`, `Destination IP`, `Timestamp`, `SimillarHTTP`, `Source Port`, `Destination Port`, `Protocol`, and `Inbound`. These variables were excluded because identifiers, addressing fields, timestamps, and testbed-specific metadata can encourage a model to learn collection-environment characteristics rather than general traffic behavior.

| Variable | Reason for removal |
|---|---|
| Unnamed: 0 | Dataset/index artifact |
| Flow ID | Flow identifier |
| Source IP | Address identifier/testbed-specific information |
| Destination IP | Address identifier/testbed-specific information |
| Timestamp | Collection-time identifier |
| SimillarHTTP | Testbed-specific/non-general flow field |
| Source Port | Endpoint identifier |
| Destination Port | Endpoint/service identifier |
| Protocol | Predetermined exclusion in the experimental design |
| Inbound | Direction/testbed metadata |

### 3.2. Missing and Infinite Values

The uploaded paper reports 129,853 genuine missing-value records removed during cleaning. Missing and non-finite observations were handled before model fitting so that invalid numerical values did not propagate into the training process.

### 3.3. Duplicate Removal

Duplicate records were removed before the train-test split. The cleaning process reduced the dataset from 3,965,133 records after missing-value handling to 19,513 unique records. Performing this operation before partitioning reduces the risk that identical observations appear in both training and holdout partitions.

This step was performed before model training because duplicate records can cause repeated observations to appear across training and testing partitions. Removing duplicates before the split reduces the possibility that the same traffic observation contributes to both model development and final evaluation.

### 3.4. Final Dataset

The final cleaned dataset contains 19,513 records. The class distribution retained from the uploaded paper is 17,886 attack records (91.66%) and 1,627 benign records (8.34%). The target is represented as a binary label: 1 for attack and 0 for benign.

| Class | Count | Proportion |
|---|---|---|
| Attack | 17,886 | 91.66% |
| Benign | 1,627 | 8.34% |
| **Total** | **19,513** | **100%** |

*Figure: Post-Cleaning Dataset Schema & Sample Records (Final 30 Features) — [chart/table image, not reproduced]*

---

## 4. Experimental Methodology

### 4.1. Overall Experimental Workflow

The updated workflow is leakage-controlled: raw data are cleaned; predetermined identifiers and artifacts are removed; the cleaned observations are partitioned into training and holdout sets; learned feature-selection and balancing operations are fitted using training information only; the Random Forest and Decision Tree are trained; and the untouched holdout set is used for final evaluation.

*Pipeline diagram (not reproduced): CICDDoS2019 DrDoS_NetBIOS raw dataset (4,094,986 rows) → Cleaning (3,965,133 rows after NaN/Inf removal) → Drop ID/leaky cols → Stratified 80/20 Train-Test Split → Training Pipeline (Under-sampling → Decision Tree / Random Forest) → Evaluation (Holdout Test / 5-Fold CV)*

Pipeline parameters shown in diagram:
- **I. Dynamic Pipeline Procedure (within CV folds)**
  - Balancing framework: imblearn.pipeline.Pipeline (fold-specific isolation)
  - Sampling strategy: RandomUnderSampler(sampling_strategy='majority')
  - Random state: 42
  - Feature selection: SelectKBest (Mutual Information, K=30)
  - Primary classifier: RandomForestClassifier (n_estimators=200, random_state=42)
- **II. Post-Split Partition Counts (80/20 Stratified)**
  - Initial Train Set (80%): 15,610 Total flows — Benign (Class 0): 1,302 flows — Attack (Class 1): 14,308 flows
  - Untouched Test Set (20%): 3,903 Total flows — Benign (Class 0): 325 flows — Attack (Class 1): 3,578 flows
- **III. Fold-Specific Training Targets**
  - Active Target Alignment: Benign (1,302) and Attack (1,302) per fold subset
  - Information Control: Zero leakage from verification folds to training pipelines

### 4.2. Train-Test Partition

The uploaded paper used a stratified 80:20 partition, producing 15,610 training records and 3,903 holdout records. The holdout set was retained for final evaluation and was not used to determine preprocessing thresholds, balancing distributions, or model parameters. If the updated notebook changed the random seed or partition counts, the final paper should replace these counts with the notebook's exact logged values before submission.

| Partition | Records | Role |
|---|---|---|
| Training | 15,610 | Model development and training-only preprocessing |
| Holdout | 3,903 | Untouched final evaluation |

### 4.3. Training-Only Class Balancing

The original experiment used training-only random under-sampling to reduce the dominance of attack observations during fitting. The previous documented configuration sampled 1,000 attack observations and 1,000 benign observations for a balanced 2,000-record learning sample. Because the updated project instructions identify the final model as a leakage-controlled pipeline but do not provide a replacement balancing count, the exact final balancing parameters must be copied from the final notebook configuration.

---

## 5. Feature Selection and Reduction

### 5.1. Initial Predictive Feature Space

After predetermined column removal, the original paper identified 77 predictive variables after excluding the target. The updated experiment changes the feature-selection stage from correlation filtering to mutual-information (MI) selection. Mutual information estimates the dependency between a feature and a discrete target; larger values indicate stronger estimated dependence, and the method is available in scikit-learn through `mutual_info_classif` [5].

### 5.2. Final Feature Set

The updated pipeline ranks candidate predictive variables using mutual information and retains the 30 highest-ranked features. This replaces the earlier 0.95 correlation filter and its 52-feature result. The purpose is to produce a compact feature representation based on estimated feature-target dependency rather than pairwise feature redundancy.

To control leakage, the feature-selection procedure must be fitted using training data only and, during cross-validation, independently within each fold. Scikit-learn's Pipeline mechanism is designed to chain preprocessing and prediction steps so that they can be fitted and cross-validated together [6].

### 5.3. Final Feature Space

The final feature space contains 30 MI-selected variables.

| Stage | Number of Features |
|---|---|
| Initial predictive | 77 |
| Correlation filtered | 52 |
| Final MI selected | 30 |

*Figure: Mutual-Information Feature Ranking and Final 30-Feature Selection*

---

## 6. Exploratory Data Analysis

### 6.1. Final Class Distribution

The cleaned dataset remains strongly attack-heavy, with 91.66% attack records and 8.34% benign records. This imbalance is why accuracy is reported together with class-specific precision, recall, F1-score, and confusion-matrix analysis. Precision-recall analysis is especially informative when class distributions are imbalanced [3].

*Figure: Final Cleaned Class Distribution — Benign: 1,627 — Attack: 17,886*

### 6.2. Network-Flow Feature Distributions

Network-flow variables can have skewed distributions and substantial ranges. Features such as packet lengths, packet rates, inter-arrival times, flow duration, flags, and window measurements provide different views of traffic behavior. The exploratory plots are descriptive and should not be treated as evidence of causality or standalone feature importance.

*Figure: Selected Network-Flow Feature Distributions*

---

## 7. Machine-Learning Models

### 7.1. Decision Tree Classifier

A Decision Tree was retained as the baseline classifier. Decision-tree induction represents classification through a sequence of feature-based splits, producing a model whose individual decision paths can be inspected relatively directly [7]. In this project, the Decision Tree provides a simpler reference against which the ensemble Random Forest can be compared.

### 7.2. Random Forest Classifier

Random Forest is the principal model. It combines multiple decision trees using randomized training and feature selection and aggregates their predictions. Breiman introduced Random Forest as an ensemble approach in which individual trees are randomized and the forest combines their outputs to improve generalization [8].

The final Random Forest uses the updated 30-feature representation and the leakage-controlled training procedure. The implementation should be documented using the exact final hyperparameters from the notebook, including the number of trees, maximum depth, split/leaf constraints, class-balancing configuration, random state, and other non-default settings.

*Figure: Decision Tree vs Final Random Forest (bar comparison across Accuracy, Attack Precision, Attack Recall, Attack F1, ROC-AUC, Average Precision) — both models shown performing near-ceiling across all metrics*

---

## 10. Random Forest Results

### 10.1. Holdout Performance

The final project specification supplied for this revision reports a Random Forest holdout accuracy of **99.51%** using the updated leakage-controlled pipeline with 30 MI-selected features.

| Metric | Historical Decision Tree result |
|---|---|
| Accuracy | 98.31% |
| Attack precision | 99.94% |
| Attack recall | 98.21% |

The reported 99.51% accuracy indicates that the model correctly classified approximately 99.51% of holdout observations in the final run. It does not, by itself, establish how errors are distributed between benign and attack traffic; the confusion matrix and class-specific metrics are therefore required for a complete cybersecurity interpretation.

> **FIGURE/DIAGRAM BLOCKER** — Insert the final Random Forest holdout confusion matrix here. This is a required result figure, not an optional decoration.

**Final Random Forest — Real Holdout Confusion Matrix**

| | Predicted Benign | Predicted Attack |
|---|---|---|
| **Actual Benign** | 325 | 0 |
| **Actual Attack** | 19 | 3,559 |

*Figure: Final Random Forest Holdout Confusion Matrix*

### 10.2. Confusion-Matrix Analysis

The confusion matrix should be interpreted in terms of true negatives (benign correctly classified), false positives (benign incorrectly classified as attack), false negatives (attack incorrectly classified as benign), and true positives (attack correctly classified). In DDoS detection, false negatives are particularly important because they represent malicious flows that are not flagged.

### 10.3. Synthetic Stress Test

The updated project includes a synthetic stress test intended to examine robustness beyond the standard holdout evaluation. A synthetic stress test is useful only when its generation procedure and expected perturbations are explicitly documented; otherwise, its results cannot be reproduced or interpreted reliably.

*Figure: Real Holdout vs Synthetic Stress Test (bar comparison across Accuracy, Benign F1, Attack Precision, Attack Recall, Attack F1, ROC-AUC, Average Precision)*

*Figure: Synthetic Stress Test — Predicted Probability of DDoS Attack (histogram, Synthetic Benign vs Synthetic Attack distributions)*

> **FIGURE/DIAGRAM BLOCKER** — Synthetic-stress-test blocker: insert the exact generation procedure, perturbation variables, sample size, random seed, expected class labels, model predictions, accuracy/precision/recall/F1 (if computed), and comparison against the ordinary holdout result. Do not invent a stress-test score.

> **FIGURE/DIAGRAM BLOCKER** — Insert the synthetic-stress-test visualization here, such as a metric comparison or prediction-distribution plot, using the exact figure generated by the final notebook.

---

## 11. Comparison of Decision Tree and Random Forest

The Decision Tree serves as the baseline while the Random Forest is the primary model. The historical Decision Tree accuracy in the uploaded paper was 98.31%, whereas the final Random Forest specification reports 99.51% holdout accuracy. Because the feature-selection method changed between the historical and final versions, the comparison should be treated as provisional until the Decision Tree is rerun under the same final 30-feature pipeline.

| Metric | Decision Tree | Random Forest |
|---|---|---|
| Holdout accuracy | 98.31% (historical) | 99.51% (final) |
| Precision | Historical value only; rerun required | Blocker |
| Recall | Historical value only; rerun required | Blocker |
| F1-score | Historical value only; rerun required | Blocker |
| ROC-AUC | Historical value only; rerun required | Blocker |

*Figure: Apple-to-Apple Comparison: Decision Tree vs. Final Random Forest — approximate values read from chart: Accuracy 0.9831/0.9951, Attack Precision 0.9994/1.0000, Attack Recall 0.9821/0.9947, Attack F1 0.9907/0.9973, ROC-AUC 0.9911/0.9998, Average Precision 0.9985/1.0000 (Decision Tree Baseline / Final Random Forest, 30 features)*

---

## 12. Random Forest Robustness and Error Analysis

Robustness is assessed through multiple views: the untouched holdout set, cross-validation on training data, and the synthetic stress test. Error analysis should focus on the operational meaning of false positives and false negatives rather than reporting only aggregate accuracy.

A false negative is an attack flow predicted as benign, while a false positive is a benign flow predicted as attack. The final error analysis must use the exact counts from the final confusion matrix.

*Figure: Robustness Error Rate Comparison: FPR vs. FNR — Decision Tree Baseline: FPR 0.615385%, FNR not labeled; Final Random Forest (30 features): FPR 0.000000%, FNR 0.531023%*

---

## 13. Cross-Validation and Model Robustness

### 13.1. Five-Fold Cross-Validation

The earlier paper used five-fold cross-validation and fitted preprocessing within each fold to reduce leakage from learned transformations. This remains the appropriate design for the updated experiment. The final report should state the mean and standard deviation for the principal evaluation metrics from the final 30-feature pipeline.

*Figure: Five-Fold Cross-Validation Robustness (Selected K=30 Configuration) — approximate values read from chart: Accuracy ≈0.99772 ±0.00022, Precision ≈0.99991 ±0.0001x, Recall ≈0.99458 ±0.0021x, F1 ≈0.99724 ±0.00xx, ROC-AUC ≈0.99988 ±0.0001x, AP ≈0.99988 ±0.0001x (Individual Fold markers + 5-Fold Mean Score bars)*

---

## 14. Feature Importance

Random Forest feature importance can be used to describe which retained variables contributed strongly to the fitted tree-splitting process. Such importance is model-level evidence rather than proof that a feature causes DDoS traffic. The final paper should distinguish predictive contribution from causal interpretation [8], [9].

> **FIGURE/DIAGRAM BLOCKER** — Feature-importance blocker: insert the final top-feature ranking from the 30-feature Random Forest. The older 52-feature paper's ranking must not be reused without confirmation.

*Figure: Final Random Forest — Top 15 Feature Importances (bar chart, descending order): Fwd Packet Length Min, Total Length of Fwd Packets, Fwd Packet Length Max, Total Backward Packets, Max Packet Length, Bwd Packets/s, Bwd IAT Max, Flow Bytes/s, Bwd Header Length, Init_Win_bytes_forward, Packet Length Variance, Bwd IAT Mean, Bwd IAT Total, Packet Length Std, URG Flag Count*

---

## 15. Feature Reduction Analysis

The updated experiment changes feature reduction from correlation filtering to mutual-information selection. The final feature space is therefore reduced from the post-cleaning predictive feature pool to 30 features selected according to estimated feature-target dependency. Scikit-learn describes mutual information as a nonnegative dependence measure and provides it for univariate feature selection [5].

The key methodological requirement is that MI scores used for model development must be learned from training data only. If the MI ranking is computed once on the full dataset before the train-test split, the holdout data can influence feature selection and the resulting estimate can be optimistic.

| Stage | Number of Features |
|---|---|
| Initial predictive | 77 |
| Correlation filtered | 52 |
| Final MI selected | 30 |

*Figure: Feature-Space Reduction Through Mutual-Information Selection*

---

## 16. Model Interpretation

### 16.1. Classification Performance

The final Random Forest achieved 99.51% holdout accuracy under the updated experimental configuration. This result indicates strong measured separation of the two classes within the evaluated holdout set, but it should be interpreted together with class-specific metrics and error counts.

### 16.2. False Negatives

False negatives represent attack flows classified as benign. Their operational importance is high in a DDoS-detection context because missed malicious traffic may continue without an alert. The exact final false-negative count was not present in the available materials and must be taken directly from the final confusion matrix.

### 16.3. False Positives

False positives represent benign flows classified as attack. They affect analyst workload and can reduce trust in a detection system. The final false-positive count must likewise be taken from the final confusion matrix rather than inferred from accuracy.

---

## 17. Discussion

### 17.1. Data Quality

The cleaning stage substantially changed the effective number of usable observations, reducing the raw data to 19,513 cleaned flows. This demonstrates why raw row counts should not automatically be treated as independent observations for model evaluation.

### 17.2. Effect of Feature Reduction

The updated MI-based selection produces a compact 30-feature representation. The methodological objective is to retain features with stronger estimated relationships to the target while reducing the computational and interpretive burden of the full feature space. The exact contribution of this change should be discussed using the final model-comparison and ablation results if available.

### 17.3. Decision Tree Versus Random Forest

The historical Decision Tree baseline achieved 98.31% accuracy, while the updated Random Forest specification reports 99.51% accuracy. However, because the feature-selection method changed, the fairest final comparison requires both models to be evaluated using the same updated pipeline.

### 17.4. Stability

Stability should be discussed from the final cross-validation results and synthetic stress test. Small fold-to-fold variation would support consistency within the training data, while stress-test degradation would identify sensitivity to distributional perturbations. Exact updated statistics are required before making a stronger claim.

---

## 18. Methodological Controls and Leakage Considerations

A central design requirement is to reduce opportunities for information leakage. The intended controls are: duplicate removal before splitting; separation of the holdout set before learned feature selection and balancing; training-only mutual-information selection; training-only class balancing; fold-specific fitting of preprocessing during cross-validation; and retention of the final holdout set for one final evaluation.

This should be described as a leakage-controlled or leakage-safe design rather than as a guarantee of mathematically perfect leakage elimination. Scikit-learn's Pipeline framework supports chaining preprocessing and estimators so that transformations can be fitted and cross-validated as part of the modeling procedure [6].

*Diagram: Leakage-Controlled Methodology Pipeline*
- Phase 1: Ingestion — Raw Dataset (4,094,986 rows), NetBIOS DDoS Profile
- Phase 2: Global Quality Cleaning — Drop ID & Leaky Cols, Replace Inf/Nulls & Deduplicate
- Critical Leakage Barrier (Random State 42) — Stratified 80/20 Train-Test Partition Split (Train: 15,610 flows / Final Holdout: 3,903 flows)
  - **A. Isolated Training Pipeline Area** (80% Train Subset): InfinityMaxImputer() → CorrelationFilter(Threshold = 0.95) → RandomUnderSampler(Majority Class) → SelectKBest (Mutual Information, K=30) → Random Forest Classifier (Outputs final metrics)
  - **B. Holdout Test Partition Branch** (20% Untouched Test): Untouched Holdout Dataset (No fit or calculation performed) → Passed directly to fitted pipeline predict() → Final Evaluation & Diagnostic Statistics

---

## Feature Importance — Full Values (Empirical Random Forest Gini Importance Metric)

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

Note: Source Port, Destination Port, Protocol, and Inbound — all previously flagged as leakage-prone — do not appear in this feature-importance list, consistent with their removal in Section 3.1.

---

## Appendix C. Holdout Confusion Matrices

**Decision Tree — Real Holdout Confusion Matrix**

| | Predicted Benign | Predicted Attack |
|---|---|---|
| **Actual Benign** | 323 | 2 |
| **Actual Attack** | 64 | 3,514 |

**Random Forest — Real Holdout Confusion Matrix**

| | Predicted Benign | Predicted Attack |
|---|---|---|
| **Actual Benign** | 325 | 0 |
| **Actual Attack** | 19 | 3,559 |

## Appendix D. Final Performance Summary

| Measure | Decision Tree | Random Forest |
|---|---|---|
| Accuracy | BLOCKER — final 30-feature rerun | 99.51% |
| Precision | BLOCKER | BLOCKER |
| Recall | BLOCKER | BLOCKER |
| F1-score | BLOCKER | BLOCKER |
| ROC-AUC | BLOCKER | BLOCKER |
| Average Precision / PR-AUC | BLOCKER | BLOCKER |

> **FIGURE/DIAGRAM BLOCKER** — Final submission blocker: replace every BLOCKER with values directly exported from the final notebook, then perform one consistency check across this appendix, Sections 9–17, the figures, the PowerPoint, and the deployed Streamlit demonstration.

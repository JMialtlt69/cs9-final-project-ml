# Gemini Prompt — Final DDoS Notebook Revision and Documentation Figure Generator

You are revising an existing Google Colab notebook for a university Machine Learning / Cybersecurity project titled:

**Leakage-Controlled Supervised Learning for DDoS Traffic Classification: A CICDDoS2019 DrDoS_NetBIOS Study**

The existing notebook is:
`Copy_of_DrDoS_NetBIOS_Leakage_Controlled_Final.ipynb`

Your task is NOT to redesign the project. Preserve the established experiment and make the notebook internally consistent, reproducible, executable in Google Colab, and suitable as the numerical source for a professional IEEE-style project paper.

IMPORTANT: Do not invent results. Do not silently change the dataset, split, preprocessing logic, selected features, or validated results. If a newly added experiment produces a different result, report the actual result.

============================================================
1. AUTHORITATIVE PROJECT CONFIGURATION
============================================================

Dataset:
CICDDoS2019 — DrDoS_NetBIOS.csv

DATA_PATH:
`/content/drive/MyDrive/CS9L_FinalProject_Files/CSV-01-12/01-12/DrDoS_NetBIOS.csv`

Constants:
- RANDOM_STATE = 42
- TEST_SIZE = 0.20
- CORRELATION_THRESHOLD = 0.95
- CV_FOLDS = 5
- RF_TREES = 200
- Cross-validation should use n_jobs=1 for the main reproducible experiment because earlier parallel execution caused resource/worker issues in Colab.
- Synthetic stress-test seed = 142
- Synthetic observations = 1,000 benign + 1,000 attack

Target:
- BENIGN = 0
- DrDoS_NetBIOS = 1

============================================================
2. VERIFIED RAW DATA AND CLEANING
============================================================

Preserve these validated values:

Raw:
- 4,094,986 rows
- 88 columns
- DrDoS_NetBIOS = 4,093,279
- BENIGN = 1,707

Drop these 10 columns:
- Unnamed: 0
- Flow ID
- Source IP
- Destination IP
- Timestamp
- SimillarHTTP
- Source Port
- Destination Port
- Protocol
- Inbound

After column removal:
4,094,986 × 78

Infinity columns:
- Flow Bytes/s
- Flow Packets/s

Replace +/- infinity with NaN.

Remove 129,853 rows containing NaN.

After NaN removal:
3,965,133 × 78

Remove 3,945,620 duplicate rows.

Final cleaned:
19,513 × 78

Predictors:
19,513 × 77

Final class distribution:
- BENIGN = 1,627
- Attack = 17,886

Do not alter these values unless the notebook is actually rerun and produces a demonstrably different result due to code/data changes.

============================================================
3. TRAIN/TEST SPLIT
============================================================

Use stratified 80/20 train-test split:
`train_test_split(..., test_size=0.20, stratify=y, random_state=42)`

Verified partition:
Training:
- 15,610
- BENIGN = 1,302
- Attack = 14,308

Holdout:
- 3,903
- BENIGN = 325
- Attack = 3,578

The holdout must remain untouched until final evaluation.

============================================================
4. LEAKAGE-CONTROLLED PIPELINE
============================================================

Every learned operation must occur inside an imblearn/sklearn-compatible pipeline and be fitted only on training data or on the current cross-validation fold.

Actual pipeline order:

1. InfinityMaxImputer
2. CorrelationFilter(threshold=0.95)
3. RandomUnderSampler(strategy='majority', random_state=42)
4. For MI models only:
   SelectKBest(mutual_info_classif, k=K)
5. Classifier

Important:
The balancing strategy is NOT a hard-coded 1,302/1,302 configuration.

The implementation must use:

`RandomUnderSampler(sampling_strategy='majority', random_state=42)`

This dynamically reduces the majority class to the current minority-class count.

The 1,302 value is only the observed benign count in the full training partition. In CV folds, the minority count may differ. Do not document 1,302 as a configured target.

Use the phrase:
**training-only / fold-specific leakage-controlled pipeline**

Do not claim "perfectly leakage-free."

============================================================
5. BASELINE EXPERIMENTS — PRESERVE
============================================================

Decision Tree baseline:
- 77 initial predictive features
- DecisionTreeClassifier(max_depth=3, random_state=42)

Verified holdout:
- Accuracy = 0.9831
- Attack precision = 0.9994
- Attack recall = 0.9821
- Attack F1 = 0.9907
- ROC-AUC = 0.9911
- AP = 0.9985
- TN=323
- FP=2
- FN=64
- TP=3514

Random Forest baseline:
- 77 features
- RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1 for reproducibility/resource safety)
- no MI selection

Verified holdout:
- Accuracy = 0.9946
- Attack precision = 1.0000
- Attack recall = 0.9941
- Attack F1 = 0.9971
- ROC-AUC = 0.9999
- AP = 1.0000
- TN=325
- FP=0
- FN=21
- TP=3557

Do not overwrite these historical baseline values.

============================================================
6. MUTUAL-INFORMATION EXPERIMENT — PRESERVE
============================================================

Candidate K values:
10, 20, 30, 40, 52

For every K:
Infinity handling -> correlation filter -> majority undersampling -> SelectKBest(mutual_info_classif,k=K) -> Random Forest

Use 5-fold StratifiedKFold:
- n_splits=5
- shuffle=True
- random_state=42
- cross_validate(..., n_jobs=1, error_score='raise')

Verified results:

K=10:
Accuracy 0.985010
Precision 0.999291
Recall 0.984345
F1 0.991760
F1 Std 0.001001
ROC-AUC 0.998380
AP 0.999778

K=20:
Accuracy 0.991224
Precision 0.999719
Recall 0.990705
F1 0.995189
F1 Std 0.001462
ROC-AUC 0.999433
AP 0.999910

K=30:
Accuracy 0.993722
Precision 0.999649
Recall 0.993500
F1 0.996564
F1 Std 0.001016
ROC-AUC 0.999501
AP 0.999916

K=40:
Accuracy 0.992441
Precision 0.999648
Recall 0.992103
F1 0.995858
F1 Std 0.001815
ROC-AUC 0.999486
AP 0.999915

K=52:
Accuracy 0.993017
Precision 0.999648
Recall 0.992732
F1 0.996176
F1 Std 0.001360
ROC-AUC 0.999482
AP 0.999914

Selection:
- Select the highest F1 within one standard error of the best.
- Tie-break by recall, AP, lower F1 standard deviation, then fewer features.

Final selected K:
30

Do not change K=30 merely to improve a later result.

============================================================
7. FINAL 30 FEATURES — PRESERVE
============================================================

The exact selected feature list is:

1. Flow Duration
2. Total Fwd Packets
3. Total Backward Packets
4. Total Length of Fwd Packets
5. Total Length of Bwd Packets
6. Fwd Packet Length Max
7. Fwd Packet Length Min
8. Bwd Packet Length Max
9. Bwd Packet Length Min
10. Bwd Packet Length Mean
11. Flow Bytes/s
12. Flow Packets/s
13. Flow IAT Mean
14. Flow IAT Min
15. Bwd IAT Total
16. Bwd IAT Mean
17. Bwd IAT Max
18. Bwd IAT Min
19. Fwd Header Length
20. Bwd Header Length
21. Bwd Packets/s
22. Max Packet Length
23. Packet Length Std
24. Packet Length Variance
25. URG Flag Count
26. Down/Up Ratio
27. Init_Win_bytes_forward
28. Init_Win_bytes_backward
29. act_data_pkt_fwd
30. min_seg_size_forward

Feature-space reduction:
77 -> 52 -> 30

============================================================
8. FINAL RANDOM FOREST — PRESERVE VERIFIED RESULT
============================================================

Final RF:
- K=30
- 30 selected features
- n_estimators=200
- random_state=42
- same leakage-controlled pipeline

Real holdout:
- Accuracy = 0.9951
- Benign precision = 0.9448
- Benign recall = 1.0000
- Benign F1 = 0.9716
- Attack precision = 1.0000
- Attack recall = 0.9947
- Attack F1 = 0.9973
- ROC-AUC = 0.9999
- AP = 1.0000
- TN=325
- FP=0
- FN=19
- TP=3559

Final 5-fold CV:
- Accuracy = 0.993722 ± 0.001852
- Precision = 0.999649 ± 0.000221
- Recall = 0.993500 ± 0.002194
- F1 = 0.996564 ± 0.001016
- ROC-AUC = 0.999501 ± 0.000813
- AP = 0.999916 ± 0.000150

============================================================
9. CRITICAL NEW EXPERIMENT — CONTROLLED 30-FEATURE DECISION TREE
============================================================

Add a new experiment AFTER the final K=30 selection has been established.

Do NOT replace the historical 77-feature Decision Tree baseline.

Create a new pipeline equivalent to the final RF pipeline:

InfinityMaxImputer
-> CorrelationFilter(0.95)
-> RandomUnderSampler(strategy='majority', random_state=42)
-> SelectKBest(mutual_info_classif, k=30)
-> DecisionTreeClassifier(max_depth=3, random_state=42)

Use the same:
- X_train / y_train
- X_test / y_test
- random state
- preprocessing
- MI selection
- balancing
- holdout

Then evaluate the controlled 30-feature Decision Tree on the exact same untouched holdout.

Calculate:
- accuracy
- benign precision/recall/F1
- attack precision/recall/F1
- ROC-AUC
- average precision
- confusion matrix
- FPR
- FNR

Also run 5-fold CV for the controlled DT using the same pipeline and CV configuration.

IMPORTANT:
The final paper must distinguish:

A. Historical/simple Decision Tree baseline = 77 features, no MI.
B. Controlled Decision Tree = same final 30-feature pipeline as the RF.
C. Final Random Forest = same final 30-feature pipeline.

The most important model comparison should be B vs C because it isolates classifier choice more fairly.

Do not call the old 77-feature comparison "apple-to-apple" anymore.

============================================================
10. SYNTHETIC STRESS TEST — PRESERVE
============================================================

Keep the existing stress test:

- Bootstrap training rows separately by class.
- 1,000 synthetic benign + 1,000 synthetic attack.
- seed=142.
- Gaussian jitter with scale = IQR × 0.05.
- If IQR=0, use training standard deviation; if still zero, use 1.
- Clip each feature to the training 1st–99th percentile range.
- Do not retrain the model.
- Evaluate the already-fitted final RF.

Verified result:
- Accuracy = 0.9710
- Benign F1 = 0.9717
- Attack precision = 0.9968
- Attack recall = 0.9450
- Attack F1 = 0.9702
- ROC-AUC = 0.9983
- AP = 0.9983
- TN=997
- FP=3
- FN=55
- TP=945

Describe this as a controlled stress test, not external validation.

============================================================
11. NOTEBOOK CONSISTENCY CORRECTIONS
============================================================

Correct the existing notebook's misleading text:

Current/old wording:
"Training balance: 1,302 samples per class"

Replace with:
"Training balance: majority-class undersampling is performed dynamically within each training fit using RandomUnderSampler(strategy='majority'). The full training partition contains 1,302 benign observations."

Also correct the `selection_config` field currently described as:
`under_sampling_per_class: 1302`

Replace with something such as:
`under_sampling_strategy: 'majority'`

Do not hard-code 1,302 as the balancing target.

Correct later CV/figure cells that use `n_jobs=-1` to use `n_jobs=1` so the documentation figures reproduce the same resource-safe configuration used by the verified experiment.

Review all markdown cells for similar outdated statements.

============================================================
12. FIGURE-GENERATOR SECTION
============================================================

Create a clearly separated final section:

# Documentation Figure Generators

Each figure must:
- be generated from actual notebook variables/results
- be saved as PNG at 300 dpi
- have a descriptive filename
- have a publication/documentation-quality title
- have readable axis labels
- have readable feature names
- avoid unnecessary decoration
- not contain fabricated values
- be reproducible by rerunning the cell

Generate at least:

1. Raw-to-cleaning data reduction figure.
2. Final cleaned class distribution.
3. Leakage-controlled methodology pipeline diagram.
4. Feature reduction 77 -> 52 -> 30.
5. MI candidate performance comparison.
6. Final RF real-holdout confusion matrix.
7. Final RF ROC curve.
8. Final RF precision-recall curve.
9. Final RF predicted probability distribution.
10. Final RF top-15 feature importance.
11. Final RF all-30 feature importance, if readable.
12. Five-fold CV robustness/stability figure.
13. Historical DT vs RF baseline comparison.
14. Controlled 30-feature DT vs controlled 30-feature RF comparison.
15. Error-rate comparison: FPR and FNR.
16. Synthetic stress-test confusion matrix.
17. Synthetic ROC.
18. Synthetic precision-recall.
19. Synthetic predicted probability distribution.
20. Real holdout vs synthetic stress-test metric comparison.
21. Final dataset schema/sample-record figure using actual data.
22. Final model/result summary table exported as CSV.
23. Controlled model-comparison table exported as CSV.

For each figure, print its final output path.

============================================================
13. FIGURE DESIGN REQUIREMENTS
============================================================

The final documentation is IEEE-style.

Prefer restrained, publication-oriented figures:
- white/light background
- readable typography
- no oversized titles
- no decorative gradients unless useful
- consistent dimensions
- consistent naming
- sufficient DPI
- avoid cramped labels

Do not rely on colors alone to communicate information.

For feature-importance plots:
- horizontal bars
- descending importance
- values shown to 4 decimals
- top 15 for the main paper
- optional all-30 appendix figure

For confusion matrices:
- annotate exact integer counts
- show Actual vs Predicted
- use the same class order: Benign, Attack

For performance comparison:
- use the same metric order across related figures.

============================================================
14. ARTIFACT EXPORTS
============================================================

Save documentation data tables as CSV files.

At minimum:
- dataset_summary.csv
- class_distribution.csv
- feature_reduction.csv
- mi_candidate_results.csv
- final_rf_holdout_metrics.csv
- final_rf_cv_metrics.csv
- final_rf_feature_importance.csv
- historical_baseline_comparison.csv
- controlled_dt_rf_comparison.csv
- controlled_dt_cv_metrics.csv
- error_analysis.csv
- synthetic_metrics.csv
- real_vs_synthetic_comparison.csv

Save figures in:
`/content/ddos_figures_final`

Save artifacts in:
`/content/ddos_artifacts`

Create a ZIP:
`/content/ddos_figures_final.zip`

Do not automatically download dozens of individual files. Create the consolidated ZIP and provide its path.

============================================================
15. DOCUMENTATION EVIDENCE OUTPUT
============================================================

Print concise final evidence blocks at the end of the notebook:

A. Dataset summary
B. Cleaning summary
C. Train/test class counts
D. MI candidate table
E. Final 30-feature list
F. Final RF holdout metrics
G. Final RF confusion matrix
H. Final RF CV metrics
I. Historical baseline comparison
J. Controlled 30-feature DT vs RF comparison
K. Error analysis
L. Synthetic stress-test metrics
M. Real vs synthetic comparison
N. Final feature importance ranking
O. List of generated figure paths

These outputs must be directly usable as the numerical source for the IEEE documentation.

============================================================
16. DO NOT DO THESE THINGS
============================================================

Do not:
- change the dataset
- change the train/test split
- use the holdout to select features
- compute MI on the entire dataset before splitting
- hard-code 1,302 as a sampling target
- claim synthetic data is external validation
- invent results
- use approximate numbers in final tables
- silently overwrite historical baseline results
- call the old 77-feature DT vs RF comparison controlled
- replace K=30 because another K happens to look better on a later metric
- use n_jobs=-1 in the main CV workflow
- create misleading figures that exaggerate small metric differences
- introduce new engineered features unless explicitly approved

There is currently no domain-derived feature engineering step. Do not invent one. Describe the transformation stage accurately as data cleaning, correlation filtering, class balancing, and feature selection.

============================================================
17. FINAL NOTEBOOK STRUCTURE
============================================================

Keep the notebook readable and separated into cells:

1. Project title and purpose
2. Imports/installations
3. Configuration
4. Dataset ingestion and raw audit
5. Cleaning
6. Cleaning/class-distribution evidence
7. Train/test split
8. Custom preprocessing classes
9. Pipeline definitions
10. Baseline models
11. Baseline evaluation
12. Baseline CV
13. MI candidate experiment
14. K-selection rule
15. Final RF training
16. Final RF holdout evaluation
17. Final RF CV
18. Final feature list
19. Synthetic stress test
20. Error analysis
21. NEW controlled 30-feature Decision Tree
22. Controlled DT vs RF comparison
23. Controlled DT CV
24. Documentation artifact exports
25. Documentation figure generators
26. Final evidence summary
27. ZIP packaging

Use separate code cells for each major operation. Do not put the entire notebook into one giant cell.

============================================================
18. FINAL VALIDATION CHECK
============================================================

Before considering the notebook complete, programmatically verify:

- Final_K == 30
- len(FINAL_FEATURES) == 30
- all final features are present in the final pipeline
- holdout size == 3,903
- holdout is not used during feature selection
- historical baseline values remain unchanged
- controlled DT uses the same preprocessing/MI/balancing as controlled RF
- CV uses n_jobs=1
- no figure references nonexistent variables
- all figure files are successfully created
- all CSV artifacts are successfully created
- final ZIP exists
- no markdown cell claims fixed 1,302/1,302 undersampling
- no final paper figure uses approximate values
- all final metrics are generated from actual variables rather than manually typed constants

Print a final validation checklist showing PASS/FAIL for each item.

The final notebook must be the authoritative executable source for the project's documentation.

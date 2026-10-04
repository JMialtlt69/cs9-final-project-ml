# DrDoS_NetBIOS Project --- Training, Validation, and Presentation Notebook Documentation

## 1. Purpose

This document records the transition from the development/training
notebook to the cleaned presentation-ready notebook and summarizes how
testing and validation are handled in the project.

The documentation is based on the verified notebook state and the final
presentation copy:

`DrDoS_NetBIOS_Leakage_Controlled_FINAL_PRESENTATION_READY.ipynb`

The computational methodology and reported model results were preserved
during presentation cleanup.

------------------------------------------------------------------------

## 2. Notebook Versions

### Development / working notebook

The original working notebook was used to develop, inspect, debug,
validate, and recover the final experiment.

During development, additional diagnostic and audit cells were
temporarily added. These included:

-   variable/object recovery checks
-   pipeline-step inspection
-   feature-importance diagnostics
-   completeness audits
-   figure audits
-   final consistency checks

These cells were useful for verification but were not all appropriate
for a presentation-facing notebook.

### Presentation-ready notebook

The presentation copy was created from the verified working notebook.

The cleanup focused on **presentation structure rather than model
modification**.

Preserved:

-   computational code
-   modeling methodology
-   existing outputs
-   model configurations
-   feature-selection procedure
-   evaluation procedure
-   generated figures
-   final verification logic

Removed:

-   redundant development/debugging audits
-   duplicate completeness checks
-   obsolete RF-step-name diagnostic logic
-   temporary figure-blocker notes

The cleaned notebook was then opened in Google Colab and successfully
run from top to bottom.

------------------------------------------------------------------------

# 3. Final Presentation Workflow

The presentation notebook follows this sequence:

**Dataset → Data quality → Holdout → Leakage-controlled preprocessing →
Baselines → MI experiment → Final features → DT/RF → Holdout diagnostics
→ CV → Error analysis → Synthetic stress test → Verification →
Limitations → Conclusion**

This ordering separates:

1.  data preparation,
2.  model development,
3.  model selection,
4.  final evaluation,
5.  robustness analysis, and
6.  interpretation.

------------------------------------------------------------------------

# 4. Does the Project Actually Include Testing?

## Yes.

Both the historical/basic models and the final models are trained and
evaluated using a genuine train/test design.

The project uses a **stratified 80/20 holdout split**:

-   Training set: **15,610 rows**
-   Test/holdout set: **3,903 rows**
-   Random state: **42**

The holdout is separated before the learned preprocessing/modeling
stages.

The project therefore has a distinct dataset partition that is used for
final holdout testing.

------------------------------------------------------------------------

# 5. Historical / Basic Model Training and Testing

The notebook trains two historical baseline models:

-   Decision Tree baseline
-   Random Forest baseline

These preserve the earlier **77-feature baseline configuration**.

### Training

The baseline models are fitted using:

`X_train, y_train`

### Testing

After training, both baselines are evaluated on:

`X_test, y_test`

The evaluation includes:

-   Accuracy
-   Precision
-   Recall
-   F1
-   ROC-AUC
-   Average Precision
-   Confusion matrix
-   FPR
-   FNR

Therefore, the historical/basic models are **not merely trained**. They
are also tested on the held-out test partition.

The baseline models provide historical reference points for comparison
with the final leakage-controlled 30-feature models.

------------------------------------------------------------------------

# 6. Final Model Training and Testing

The final Random Forest is trained using the training partition:

`X_train, y_train`

Its pipeline is:

**InfinityMaxImputer → CorrelationFilter → RandomUnderSampler →
SelectKBest → RandomForestClassifier**

Final configuration:

-   Correlation threshold: **0.95**
-   Mutual Information feature count: **30**
-   Random Forest trees: **200**
-   Random state: **42**
-   Training-only majority-class undersampling

The final Random Forest is then evaluated on the untouched real holdout:

`X_test, y_test`

### Final real-holdout result

-   Accuracy: **99.5132%**
-   Attack precision: **100.0000%**
-   Attack recall: **99.4690%**
-   Attack F1: **99.7338%**
-   ROC-AUC: **99.9887%**
-   Average Precision: **99.9989%**
-   TN: **325**
-   FP: **0**
-   FN: **19**
-   TP: **3,559**
-   FPR: **0%**
-   FNR: **0.5310%**

The confusion matrix totals **3,903**, matching the complete holdout
set.

------------------------------------------------------------------------

# 7. Cross-Validation

The final model also uses **5-fold cross-validation on the training
partition**.

The purpose is different from the final holdout test:

### Cross-validation

Used for:

-   model/feature-selection stability
-   estimating training-partition performance across folds
-   selecting the MI feature count
-   checking variability across folds

### Final holdout

Used for:

-   final real-data evaluation
-   reporting performance on data not used during training or
    cross-validation

The final reported real-holdout metrics therefore remain separate from
the cross-validation estimates.

------------------------------------------------------------------------

# 8. Mutual Information Feature Selection

Candidate feature counts were evaluated at:

-   10
-   20
-   30
-   40
-   52

The selection was performed using training data and 5-fold
cross-validation.

The one-standard-error selection rule identified K=30 as the final
choice after considering performance, recall/AP, stability, and
feature-count efficiency.

Final selected feature count:

**30**

------------------------------------------------------------------------

# 9. Controlled Decision Tree Comparison

A controlled Decision Tree was trained using the same final 30-feature
methodology.

Configuration:

-   Decision Tree
-   `max_depth=3`
-   random state = 42
-   same leakage-controlled preprocessing
-   same 30 MI-selected features

It was evaluated on the same real holdout as the final Random Forest.

This provides a controlled model comparison rather than comparing models
under different feature-selection or preprocessing conditions.

------------------------------------------------------------------------

# 10. Synthetic Stress Test

The notebook also evaluates the final Random Forest on a controlled
synthetic stress test.

The synthetic data are generated from the training partition by:

-   class-specific bootstrap sampling
-   Gaussian jitter
-   IQR-based scale
-   fallback standard deviation when necessary
-   clipping to the 1st--99th training percentiles
-   1,000 synthetic samples per class
-   seed = 142

Total synthetic evaluation set:

**2,000 samples**

This is a **stress/robustness experiment**, not external real-world
validation.

It must therefore not be described as an independent real-world test
set.

------------------------------------------------------------------------

# 11. Final Verification

The presentation notebook retains a consolidated final verification
rather than the many development-time audits.

The verification confirms key project invariants, including:

-   77 initial predictive features
-   52 features after correlation filtering
-   K=30
-   30 final features
-   training-only majority undersampling
-   Random Forest with 200 trees
-   correct holdout size
-   correct holdout class counts
-   correct synthetic-test size
-   required artifacts present

The cleaned notebook was successfully executed in Google Colab from top
to bottom after the presentation refactor.

------------------------------------------------------------------------

# 12. Why the Presentation Version Has Fewer Validation Cells

The development notebook contained several overlapping validation and
recovery cells because the project was being audited and debugged.

Those checks were valuable during development, but keeping every
diagnostic in the final presentation would make the workflow appear
repetitive and harder to follow.

The presentation version therefore uses:

-   the actual modeling/evaluation outputs where they belong in the
    workflow, and
-   one consolidated final verification section at the end.

This preserves verification without making the presentation notebook
look like a debugging log.

------------------------------------------------------------------------

# 13. Important Methodology Boundary

The following should remain unchanged unless a genuine methodological
error is discovered:

-   train/test split
-   random state = 42
-   correlation threshold = 0.95
-   training-only undersampling
-   MI candidate values
-   one-standard-error selection procedure
-   final K=30
-   final 30 features
-   Random Forest = 200 trees
-   controlled Decision Tree = max_depth 3
-   5-fold CV
-   synthetic stress-test procedure

The presentation cleanup is a **documentation and organization change,
not a new modeling experiment**.

------------------------------------------------------------------------

# 14. Current Project Status

The computational project has reached a stable state.

The corrected final audit produced:

**39 PASS · 0 REVIEW · 0 FAIL**

The presentation notebook was subsequently executed successfully in
Google Colab.

Therefore the recommended next phase is **documentation**, not another
modeling iteration.

The documentation, report, presentation, and reviewer/Q&A materials
should all use the verified notebook results as their source of truth.

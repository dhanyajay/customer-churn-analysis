# Project Technical Report: Advanced Customer Churn Prediction Framework

## 1. Project Overview & Business Value
This project focuses on the development of a predictive intelligence system designed to minimize revenue attrition (churn) in a B2B service-based environment. Unlike traditional binary churn models (Churn/No-Churn), this framework utilizes **Multiclass Segmentation** to distinguish between healthy customers, those at high risk (direct churn), and those in a "transitionary" state who may require targeted nurturing.

By integrating state-of-the-art machine learning techniques with a structured data engineering pipeline, this system provides actionable intelligence that allows the retention team to intervene before revenue loss occurs.

---

## 2. Strategic Data Engineering: The Medallion Architecture

We adopted the **Medallion Architecture** to ensure data reliability and a single source of truth (SSOT).

### 2.1 Why the Medallion Pattern?
In industrial data science, raw data is often noisy, inconsistent, and improperly structured.
- **🥉 Bronze Layer (Ingestion)**: Stores the raw data as-is from source systems. This ensures that if the downstream logic needs to change, we can re-process from the source without loss.
- **🥈 Silver Layer (Standardization)**: This is where we standardise column naming (snake_case), unify date formats, and resolve data quality issues (null imputation). **Why?** Uniform schemas prevent breaking downstream models and enable clean data joining between agreements and retention cases.
- **🥇 Gold Layer (Refinement)**: The production-ready layer. Here, we apply business rules, filter for high-value features, and enforce **strict data leakage isolation**. This ensures the model learns only from information available *at the time of prediction*.

---

## 3. High-Fidelity Feature Engineering

### 3.1 The "Data Leakage" Isolation Protocol
Data leakage is the primary reason models fail in production. We systematically identified and removed the following categories of features:
- **Direct Churn Signals**: Columns like `lost_agreements` or `resolution_status` provide a perfect but useless 1.0 correlation because they are determined *after* the churn event.
- **Case Management Metadata**: `case_creation_date` or `resolved_date` provide hindsight bias.
- **Proxy Leakage**: Excluded repair/service case history if those cases were opened as a consequence of the churn intent (circular logic).

### 3.2 Feature Synthesis (The Value Add)
We moved beyond raw counts to derived ratios that capture customer behavior:
- **`tenure_days`**: Captures long-term loyalty.
- **`contract_duration`**: Measures the stability of the contract.
- **`duration_to_tenure_ratio`**: A critical innovation. It measures how much of the original commitment remains. Customers nearing the end of their contract with a low tenure are statistically the highest risk factor.

---

## 4. Class Imbalance: Strategic Management

B2B churn datasets are almost always imbalanced (loyal customers outnumber churners).

### 4.1 Why not full Undersampling?
Full undersampling would reduce our dataset to the size of the smallest class (~1,000 samples), discarding 90% of our useful data.
### 4.2 Our Approach: Hybrid Balancing
1. **Controlled Undersampling**: We reduced the majority class (Class 2) by a factor of 3 to narrow the gap without losing the distribution's "signal."
2. **Loss Function Weighting**: We utilized **Scale Pos Weight / Class Weights**. 
   - **Rationale**: By telling the model that Class 1 (Churn) is "4x more expensive to miss" than Class 2, the loss function penalizes mistakes on the minority class more severely. This forces the model to learn the specific characteristics of churners rather than just guessing the majority class for high accuracy.

---

## 5. Modeling Philosophy: Why LightGBM?

We chose **LightGBM (LGBM)** over competitors (XGBoost/CatBoost) for several industry-specific reasons:
- **Leaf-wise Growth**: Unlike XGBoost's depth-wise growth, LGBM's leaf-wise strategy reduces loss much faster on large, heterogeneous datasets.
- **Native Categorical Support**: LGBM handles categorical variables (like `branch`, `line_of_business`) without needing extensive one-hot encoding, which prevents "curse of dimensionality" issues.
- **Speed & Efficiency**: LGBM trains significantly faster, allowing for more extensive hyperparameter optimization (Optuna) in shorter timeframes.

---

## 6. Optimization: Bayesian Hyperparameter Search (Optuna)

Typical grid searches are inefficient because they test "unlikely" regions. We implemented **Optuna** for Bayesian Optimization.

### 6.1 Why Bayesian Search?
It uses past trial results to build a probability model of which hyperparameter regions perform best. This "directed search" allows us to find high-performing configurations (e.g., `num_leaves=50`, `learning_rate=0.046`) in fewer trials than random or grid searching.

### 6.2 Target Metric: Macro F1-Score
We optimized for **Macro F1** rather than Accuracy. 
- **Reasoning**: In an imbalanced dataset, a model can have 90% accuracy by never predicting churn. Macro F1 calculates the F1-score for each class independently and averages it, ensuring that the model *must* perform well on the minority churn class to achieve a high score.

---

## 7. Model Explainability: Interpreting the "Black Box"

Post-training, we utilize **SHAP (SHapley Additive exPlanations)** for two reasons:
1. **Global Transparency**: Identifying which features drive the model's overall logic (e.g., `tenure_days` is the #1 predictor).
2. **Local Interpretability**: For a specific high-risk account, SHAP can tell the retention team *exactly why* that customer is flagged (e.g., "This customer is 2x more likely to churn because their machine repair cases spiked while their contract is 90% complete").

---

## 8. Final Evaluation & Business Impact

### 8.1 Metrics Summary
- **Overall Accuracy**: 81.6% (Strength in generalization)
- **Macro F1**: 0.75 (Balanced performance)
- **Class 2 Precision**: 100% (Zero false alarms on healthy customers)
- **Class 1 Recall**: ~70% (Successfully identifying 7 out of 10 churners)

### 8.2 Strategic Recommendation
The model has a slight tendency to misclassify Class 0 (Intermediate) as Class 1 (Churn). This is a **calculated risk**; it is cheaper to offer an incentive to an intermediate customer than to lose a high-risk churner.

---

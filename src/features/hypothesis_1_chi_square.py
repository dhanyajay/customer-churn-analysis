import pandas as pd
from scipy.stats import chi2_contingency

class Hypothesis1ChiSquare:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 1: Categorical features are independent of churn category
        Test: Chi-Square Test of Independence
        Why: Used for categorical variables to test if there's a significant association
        between the feature and the target variable. Assumptions: Random sampling,
        independence of observations, expected frequency >=5 in at least 80% of cells.
        """
        print("Hypothesis 1: Categorical Independence (Chi-Square Test)")
        print("Null: Feature is independent of churn category")
        print("Alternative: Feature is dependent on churn category")

        categorical_features = ['retention_customer_tier', 'retention_case_type', 'retention_pull_type',
                                'retention_current_status', 'retention_resolution_status', 'renewal_type']

        results = []
        for feature in categorical_features:
            if feature in self.data.columns:
                test_subset = self.data[[feature, self.target]].dropna()
                if len(test_subset) > 0 and len(test_subset[feature].unique()) > 1:
                    contingency_table = pd.crosstab(test_subset[feature], test_subset[self.target])
                    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                    significant = p_value < 0.05
                    results.append({
                        'Feature': feature,
                        'Test': 'Chi-Square',
                        'Statistic': chi2,
                        'P-Value': p_value,
                        'Significant': significant
                    })

        return results
import pandas as pd
from scipy.stats import f_oneway

class Hypothesis2ANOVA:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 2: No difference in means of continuous features across churn categories
        Test: One-way ANOVA
        Why: Parametric test for comparing means across multiple groups. Assumptions:
        Normality, homoscedasticity, independence. Used when data meets parametric assumptions.
        """
        print("Hypothesis 2: Difference in Means (ANOVA)")
        print("Null: No significant difference in feature means across churn categories")
        print("Alternative: Significant difference exists")

        continuous_features = ['total_agreements', 'active_agreements', 'lost_agreements',
                               'avg_fee_bob', 'total_revenue_bob']

        results = []
        for feature in continuous_features:
            if feature in self.data.columns:
                test_subset = self.data[[feature, self.target]].dropna()
                if len(test_subset) > 0:
                    groups = [group[feature].values for name, group in test_subset.groupby(self.target)]
                    if len(groups) > 1:
                        f_stat, p_value = f_oneway(*groups)
                        significant = p_value < 0.05
                        results.append({
                            'Feature': feature,
                            'Test': 'ANOVA',
                            'Statistic': f_stat,
                            'P-Value': p_value,
                            'Significant': significant
                        })

        return results
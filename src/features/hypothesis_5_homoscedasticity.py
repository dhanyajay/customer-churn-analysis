import pandas as pd
from scipy.stats import levene

class Hypothesis5Homoscedasticity:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 5: Equal variances across churn categories for continuous features
        Test: Levene's Test
        Why: Tests homoscedasticity assumption for ANOVA. More robust than Bartlett's
        test against departures from normality. Used to validate ANOVA assumptions.
        """
        print("Hypothesis 5: Homoscedasticity (Levene's Test)")
        print("Null: Equal variances across churn categories")
        print("Alternative: Unequal variances across churn categories")

        continuous_features = ['total_agreements', 'active_agreements', 'lost_agreements',
                               'avg_fee_bob', 'total_revenue_bob']

        results = []
        for feature in continuous_features:
            if feature in self.data.columns:
                test_subset = self.data[[feature, self.target]].dropna()
                if len(test_subset) > 0:
                    groups = [group[feature].values for name, group in test_subset.groupby(self.target)]
                    if len(groups) > 1:
                        stat, p_value = levene(*groups)
                        equal_var = p_value > 0.05
                        results.append({
                            'Feature': feature,
                            'Test': 'Levene',
                            'Statistic': stat,
                            'P-Value': p_value,
                            'Equal_Variance': equal_var
                        })

        return results
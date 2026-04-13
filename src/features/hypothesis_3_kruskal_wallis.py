import pandas as pd
from scipy.stats import kruskal

class Hypothesis3KruskalWallis:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 3: No difference in distributions of continuous features across churn categories
        Test: Kruskal-Wallis H-test
        Why: Non-parametric alternative to ANOVA when normality assumption is violated.
        Tests if samples come from the same distribution. No assumptions about normality.
        """
        print("Hypothesis 3: Non-parametric Difference (Kruskal-Wallis)")
        print("Null: No significant difference in feature distributions across churn categories")
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
                        h_stat, p_value = kruskal(*groups)
                        significant = p_value < 0.05
                        results.append({
                            'Feature': feature,
                            'Test': 'Kruskal-Wallis',
                            'Statistic': h_stat,
                            'P-Value': p_value,
                            'Significant': significant
                        })

        return results
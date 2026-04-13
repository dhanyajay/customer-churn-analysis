import numpy as np
import pandas as pd
from scipy.stats import f_oneway

class Hypothesis3PermutationTest:
    def __init__(self, data, target_column='churn_category', n_permutations=1000, random_state=42):
        self.data = data.copy()
        self.target = target_column
        self.n_permutations = n_permutations
        self.random_state = np.random.RandomState(random_state)

    def _compute_f_statistic(self, groups):
        return f_oneway(*groups)[0]

    def _permutation_p_value(self, feature_values, labels):
        observed_labels = np.unique(labels)
        observed_groups = [feature_values[labels == label] for label in observed_labels]
        observed_stat = self._compute_f_statistic(observed_groups)

        permuted_stats = []
        for _ in range(self.n_permutations):
            permuted = self.random_state.permutation(labels)
            perm_groups = [feature_values[permuted == label] for label in observed_labels]
            permuted_stats.append(self._compute_f_statistic(perm_groups))

        permuted_stats = np.array(permuted_stats)
        p_value = (np.sum(permuted_stats >= observed_stat) + 1) / (len(permuted_stats) + 1)
        return observed_stat, p_value

    def run_test(self):
        """
        Hypothesis 3: No difference in distributions of continuous features across churn categories
        Test: Permutation test using the F-statistic
        Why: Distribution-free alternative to parametric ANOVA and Kruskal-Wallis.
        Useful when normality assumptions are unclear and group variances may differ.
        """
        print("Hypothesis 3: Non-parametric Difference (Permutation Test)")
        print("Null: No significant difference in feature distributions across churn categories")
        print("Alternative: Significant difference exists")

        continuous_features = ['total_agreements', 'active_agreements', 'lost_agreements',
                               'avg_fee_bob', 'total_revenue_bob']

        results = []
        for feature in continuous_features:
            if feature in self.data.columns:
                test_subset = self.data[[feature, self.target]].dropna()
                if len(test_subset) > 0:
                    feature_values = test_subset[feature].to_numpy()
                    labels = test_subset[self.target].astype('category').cat.codes.to_numpy()
                    unique_labels = np.unique(labels)
                    if len(unique_labels) > 1:
                        stat, p_value = self._permutation_p_value(feature_values, labels)
                        significant = p_value < 0.05
                        results.append({
                            'Feature': feature,
                            'Test': 'Permutation ANOVA',
                            'Statistic': stat,
                            'P-Value': p_value,
                            'Significant': significant
                        })

        return results
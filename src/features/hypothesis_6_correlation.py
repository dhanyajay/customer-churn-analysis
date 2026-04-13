import pandas as pd
from scipy.stats import pearsonr, spearmanr

class Hypothesis6Correlation:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 6: No linear/monotonic correlation between continuous features and churn
        Test: Pearson/Spearman Correlation
        Why: Measures strength and direction of relationship. Pearson for linear,
        Spearman for monotonic. Used to identify features with strong relationships to target.
        """
        print("Hypothesis 6: Correlation Analysis")
        print("Null: No correlation between feature and churn")
        print("Alternative: Significant correlation exists")

        # For simplicity, convert churn to numeric (0: No Churn, 1: Partial, 2: Full)
        churn_numeric = self.data[self.target].map({'No Churn': 0, 'Partial Churn': 1, 'Full Churn': 2})

        continuous_features = ['total_agreements', 'active_agreements', 'lost_agreements',
                               'avg_fee_bob', 'total_revenue_bob']

        results = []
        for feature in continuous_features:
            if feature in self.data.columns:
                test_subset = pd.DataFrame({feature: self.data[feature], 'churn': churn_numeric}).dropna()
                if len(test_subset) > 0:
                    # Pearson correlation
                    pearson_corr, pearson_p = pearsonr(test_subset[feature], test_subset['churn'])
                    # Spearman correlation
                    spearman_corr, spearman_p = spearmanr(test_subset[feature], test_subset['churn'])

                    results.append({
                        'Feature': feature,
                        'Pearson_Corr': pearson_corr,
                        'Pearson_P': pearson_p,
                        'Spearman_Corr': spearman_corr,
                        'Spearman_P': spearman_p
                    })

        return results
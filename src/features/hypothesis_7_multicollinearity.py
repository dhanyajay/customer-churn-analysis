import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class Hypothesis7Multicollinearity:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 7: No multicollinearity among continuous features
        Test: Variance Inflation Factor (VIF)
        Why: Detects multicollinearity in regression models. VIF > 5-10 indicates
        problematic multicollinearity. Used to ensure feature independence in modeling.

        Note: total_agreements = active_agreements + lost_agreements creates
        perfect collinearity (VIF = inf). This is expected and should be handled
        by dropping total_agreements in feature selection.
        """
        print("Hypothesis 7: Multicollinearity Check (VIF)")
        print("Null (H₀): No multicollinearity among continuous predictors (VIF ≤ 5)")
        print("Alternative (H₁): Multicollinearity exists (VIF > 5)")

        continuous_features = ['total_agreements', 'active_agreements', 'lost_agreements',
                               'avg_fee_bob', 'total_revenue_bob']

        # Filter to numeric columns that exist
        available = [f for f in continuous_features if f in self.data.columns]
        vif_data = self.data[available].dropna()

        results = []
        if len(vif_data) > 0:
            for feature in available:
                y = vif_data[feature].to_numpy()
                X = vif_data.drop(columns=[feature]).to_numpy()
                if X.shape[1] == 0:
                    continue

                model = LinearRegression().fit(X, y)
                r2 = model.score(X, y)
                if r2 >= 0.999999:
                    vif = np.inf
                else:
                    vif = 1.0 / (1.0 - r2)

                problematic = vif > 5
                result = 'Reject H0' if problematic else 'Fail to reject H0'

                # Determine explanation notes
                if np.isinf(vif) or r2 >= 0.999999:
                    notes = 'Perfect collinearity detected (total = active + lost)'
                elif vif > 10:
                    notes = 'Severe multicollinearity – consider dropping'
                elif vif > 5:
                    notes = 'Moderate multicollinearity – investigate'
                else:
                    notes = 'No multicollinearity concern'

                results.append({
                    'Feature': feature,
                    'VIF': round(vif, 4) if not np.isinf(vif) else np.inf,
                    'Problematic': problematic,
                    'Result': result,
                    'Notes': notes
                })

        return results
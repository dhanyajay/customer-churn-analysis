import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt


class Hypothesis4Normality:
    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    def run_test(self):
        """
        Hypothesis 4: Continuous features follow normal distribution
        Method: Q-Q Plots + Histograms + Skewness/Kurtosis metrics

        Visual approach using Q-Q plots and histograms is more intuitive and
        reliable for large datasets than Shapiro-Wilk (which warns for N > 5000).
        Skewness and Kurtosis values provide numeric backup:
          - Skewness: |skew| < 2 is roughly acceptable
          - Kurtosis: |kurt| < 7 is roughly acceptable
        """
        print("Hypothesis 4: Normality Assumption Check")
        print("Null (H₀): Feature follows a normal distribution")
        print("Alternative (H₁): Feature does NOT follow a normal distribution")
        print("Method: Q-Q Plots + Histograms + Skewness/Kurtosis\n")

        continuous_features = [
            'total_agreements', 'active_agreements', 'lost_agreements',
            'avg_fee_bob', 'total_revenue_bob'
        ]

        results = []
        features_to_plot = []

        for feature in continuous_features:
            if feature in self.data.columns:
                values = self.data[feature].dropna()
                if len(values) >= 3:
                    skewness = values.skew()
                    kurtosis = values.kurtosis()

                    # Threshold-based conclusion
                    # |skew| < 2 and |kurtosis| < 7 → approximately normal
                    is_normal = abs(skewness) < 2 and abs(kurtosis) < 7
                    result = 'Fail to reject H0' if is_normal else 'Reject H0'

                    results.append({
                        'Feature': feature,
                        'Test': 'Skewness-Kurtosis + Q-Q Plot',
                        'Skewness': round(skewness, 4),
                        'Kurtosis': round(kurtosis, 4),
                        'Normal': is_normal,
                        'Result': result
                    })
                    features_to_plot.append(feature)

        # Generate Q-Q plots and histograms
        if features_to_plot:
            self._plot_normality(features_to_plot)

        return results

    def _plot_normality(self, features):
        """Generate Q-Q plots and histograms side by side for each feature."""
        n_features = len(features)
        fig, axes = plt.subplots(n_features, 2, figsize=(14, 4 * n_features))

        if n_features == 1:
            axes = axes.reshape(1, -1)

        for i, feature in enumerate(features):
            values = self.data[feature].dropna()

            # Histogram with KDE
            axes[i, 0].hist(values, bins=50, density=True, alpha=0.7,
                            color='steelblue', edgecolor='white')
            # Overlay normal curve
            mu, sigma = values.mean(), values.std()
            x_range = np.linspace(values.min(), values.max(), 200)
            axes[i, 0].plot(x_range, stats.norm.pdf(x_range, mu, sigma),
                            'r-', linewidth=2, label='Normal Fit')
            axes[i, 0].set_title(f'Histogram: {feature}', fontsize=11, fontweight='bold')
            axes[i, 0].set_xlabel(feature)
            axes[i, 0].set_ylabel('Density')
            axes[i, 0].legend()

            # Q-Q Plot
            stats.probplot(values, dist="norm", plot=axes[i, 1])
            axes[i, 1].set_title(f'Q-Q Plot: {feature}', fontsize=11, fontweight='bold')
            axes[i, 1].get_lines()[0].set(markerfacecolor='steelblue',
                                           markeredgecolor='steelblue', markersize=3)
            axes[i, 1].get_lines()[1].set(color='red', linewidth=2)

        plt.tight_layout()
        plt.show()
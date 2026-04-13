import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


class NormalityPlots:
    """
    Reusable normality visualization functions.
    Generates Q-Q plots and histograms with normal curve overlay
    for checking the normality assumption of continuous features.
    """

    def __init__(self, data):
        self.data = data.copy()

    def plot_qq_and_histogram(self, features):
        """
        Generate side-by-side Q-Q plots and histograms for the given features.

        Args:
            features: list of column names to check for normality
        """
        valid_features = [f for f in features if f in self.data.columns]
        n = len(valid_features)
        if n == 0:
            print("No valid features found to plot.")
            return

        fig, axes = plt.subplots(n, 2, figsize=(14, 4 * n))
        if n == 1:
            axes = axes.reshape(1, -1)

        for i, feature in enumerate(valid_features):
            values = self.data[feature].dropna()

            # --- Histogram with normal curve overlay ---
            axes[i, 0].hist(values, bins=50, density=True, alpha=0.7,
                            color='steelblue', edgecolor='white')
            mu, sigma = values.mean(), values.std()
            x_range = np.linspace(values.min(), values.max(), 200)
            axes[i, 0].plot(x_range, stats.norm.pdf(x_range, mu, sigma),
                            'r-', linewidth=2, label='Normal Fit')
            axes[i, 0].set_title(f'Histogram: {feature}',
                                 fontsize=11, fontweight='bold')
            axes[i, 0].set_xlabel(feature)
            axes[i, 0].set_ylabel('Density')
            axes[i, 0].legend()

            # --- Q-Q Plot ---
            stats.probplot(values, dist="norm", plot=axes[i, 1])
            axes[i, 1].set_title(f'Q-Q Plot: {feature}',
                                 fontsize=11, fontweight='bold')
            axes[i, 1].get_lines()[0].set(markerfacecolor='steelblue',
                                           markeredgecolor='steelblue',
                                           markersize=3)
            axes[i, 1].get_lines()[1].set(color='red', linewidth=2)

        plt.tight_layout()
        plt.show()

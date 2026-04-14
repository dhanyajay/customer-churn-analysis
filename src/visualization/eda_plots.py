import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class EDAPlots:
    """
    Reusable EDA visualization functions for the Silver Layer.
    Provides box plots, density/KDE plots, correlation heatmap,
    and categorical bar charts grouped by a target variable.
    """

    def __init__(self, data, target_column='churn_category'):
        self.data = data.copy()
        self.target = target_column

    # ------------------------------------------------------------------ #
    #  Distribution Plots (Histogram + KDE overlay by churn category)
    # ------------------------------------------------------------------ #
    def plot_distributions(self, features=None):
        """
        Histogram + KDE density overlay for continuous features,
        split by churn category. Limits x-axis to 95th percentile context.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != self.target]

        n = len(features)
        fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n))
        if n == 1:
            axes = [axes]

        categories = self.data[self.target].dropna().unique()
        palette = sns.color_palette("Set2", len(categories))

        for i, feature in enumerate(features):
            for j, cat in enumerate(categories):
                subset = self.data[self.data[self.target] == cat][feature].dropna()
                axes[i].hist(subset, bins=50, alpha=0.5, density=True,
                             label=cat, color=palette[j], edgecolor='white')
            
            axes[i].set_title(f'Distribution of {feature} by Churn Category',
                              fontsize=12, fontweight='bold')
            # Limit the x-axis to the 95th percentile to make the distributions visible
            upper_limit = self.data[feature].quantile(0.95)
            if upper_limit > self.data[feature].min():
                axes[i].set_xlim(self.data[feature].min(), upper_limit)
                
            axes[i].set_xlabel(feature)
            axes[i].set_ylabel('Density')
            axes[i].legend()

            # Dynamic conclusions based on simple averages
            overall_mean = self.data[feature].mean()
            churners = self.data[self.data[self.target] == 'Full Churn'][feature]
            churn_mean = churners.mean() if not churners.empty else 0
            direction = "higher" if churn_mean > overall_mean else "lower"
            print(f"Conclusion for {feature}: On average, Full Churn customers have {direction} values "
                  f"({churn_mean:.2f}) compared to the overall average ({overall_mean:.2f}). "
                  f"[Plot clipped at 95th percentile: {upper_limit:.2f} for visibility]")

        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    #  Box Plots
    # ------------------------------------------------------------------ #
    def plot_boxplots(self, features=None):
        """
        Box plots for continuous features grouped by churn category.
        Displays clearly by removing extreme outliers from the visual geometry.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != self.target]

        n = len(features)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 6))
        if n == 1:
            axes = [axes]

        for i, feature in enumerate(features):
            # showfliers=False resolves the squashed boxplot visualization issue
            sns.boxplot(data=self.data, x=self.target, y=feature,
                        ax=axes[i], palette='Set2',
                        order=['No Churn', 'Partial Churn', 'Full Churn'],
                        showfliers=False)
            axes[i].set_title(f'{feature}', fontsize=11, fontweight='bold')
            axes[i].set_xlabel('Churn Category')
            axes[i].tick_params(axis='x', rotation=15)
            print(f"Boxplot Conclusion for {feature}: The plot excludes outliers to reveal the core "
                  f"interquartile range and median differences across the churn categories clearly.")

        plt.suptitle('Box Plots of Continuous Features by Churn Category (Outliers Hidden)',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    #  Density Plots (KDE)
    # ------------------------------------------------------------------ #
    def plot_density(self, features=None):
        """
        KDE density plots for continuous features by churn category.
        Avoids drawing outside natural boundaries by using seaborn cleanly.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != self.target]

        n = len(features)
        fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n))
        if n == 1:
            axes = [axes]

        for i, feature in enumerate(features):
            valid_data = self.data.dropna(subset=[feature, self.target])
            if not valid_data.empty:
                # Use Seaborn's kdeplot for better appealing graphs, fill visual, and boundaries
                sns.kdeplot(data=valid_data, x=feature, hue=self.target,
                            ax=axes[i], fill=True, common_norm=False, cut=0,
                            palette='Set2', linewidth=2, warn_singular=False)
            
            axes[i].set_title(f'Density Plot: {feature}', fontsize=12, fontweight='bold')
            
            upper_limit = self.data[feature].quantile(0.95)
            if upper_limit > self.data[feature].min():
                axes[i].set_xlim(self.data[feature].min(), upper_limit)
                
            axes[i].set_xlabel(feature)
            print(f"Density Conclusion for {feature}: KDE curve shows the probability density up to the 95th percentile, highlighting the dominant distribution shapes per category.")

        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    #  Correlation Heatmap
    # ------------------------------------------------------------------ #
    def plot_correlation_heatmap(self, features=None):
        """
        Correlation heatmap of numeric features showing the full grid.
        Also explicitly extracts and prints highest parameter correlations.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()

        corr_matrix = self.data[features].corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Remove masking. The user explicitly requested to view the full diagonal and top triangle.
        sns.heatmap(corr_matrix, annot=True, fmt='.3f',
                    cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                    square=True, linewidths=0.5, ax=ax,
                    cbar_kws={"shrink": 0.8})
        ax.set_title('Correlation Heatmap (Numeric Features)',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

        # Present the correlation metrics specifically
        print("\n--- Correlation Metrics ---")
        corr_pairs = corr_matrix.unstack().dropna()
        # Remove self-correlation of 1.0 (diagonal)
        corr_pairs = corr_pairs[corr_pairs != 1.0]
        # Sort by absolute correlation
        sorted_pairs = corr_pairs.reindex(corr_pairs.abs().sort_values(ascending=False).index).drop_duplicates()
        print("Top 10 most correlated feature pairs:")
        print(sorted_pairs.head(10))
        print("\nCorrelation Conclusion: Look for highly correlated feature pairs (|corr| > 0.70) as they might indicate multicollinearity which can negatively impact some models.")

        return corr_matrix

    # ------------------------------------------------------------------ #
    #  Categorical Bar Charts
    # ------------------------------------------------------------------ #
    def plot_categorical_bars(self, features=None):
        """
        Stacked/grouped bar charts for categorical features by churn category.
        """
        if features is None:
            features = self.data.select_dtypes(include=['object', 'category']).columns.tolist()
            features = [f for f in features if f != self.target and f != 'account_number']

        n = len(features)
        if n == 0:
            print("No categorical features to plot.")
            return

        fig, axes = plt.subplots(n, 1, figsize=(12, 5 * n))
        if n == 1:
            axes = [axes]

        for i, feature in enumerate(features):
            ct = pd.crosstab(self.data[feature], self.data[self.target], normalize='index') * 100
            ct = ct.reindex(columns=['No Churn', 'Partial Churn', 'Full Churn'], fill_value=0)
            ct.plot(kind='barh', stacked=True, ax=axes[i], colormap='Set2',
                    edgecolor='white', linewidth=0.5)
            axes[i].set_title(f'{feature} vs Churn Category (%)',
                              fontsize=12, fontweight='bold')
            axes[i].set_xlabel('Percentage (%)')
            axes[i].legend(title='Churn Category', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Additional conclusion piece
            print(f"Categorical Conclusion for {feature}: Proportions show how the composition of churn states varies across different categories of {feature}.")

        plt.tight_layout()
        plt.show()

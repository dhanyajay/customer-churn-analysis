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
        split by churn category.
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
            axes[i].set_xlabel(feature)
            axes[i].set_ylabel('Density')
            axes[i].legend()

        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    #  Box Plots
    # ------------------------------------------------------------------ #
    def plot_boxplots(self, features=None):
        """
        Box plots for continuous features grouped by churn category.
        Useful for spotting distribution differences and outliers.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != self.target]

        n = len(features)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 6))
        if n == 1:
            axes = [axes]

        for i, feature in enumerate(features):
            sns.boxplot(data=self.data, x=self.target, y=feature,
                        ax=axes[i], palette='Set2',
                        order=['No Churn', 'Partial Churn', 'Full Churn'])
            axes[i].set_title(f'{feature}', fontsize=11, fontweight='bold')
            axes[i].set_xlabel('Churn Category')
            axes[i].tick_params(axis='x', rotation=15)

        plt.suptitle('Box Plots of Continuous Features by Churn Category',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    #  Density Plots (KDE)
    # ------------------------------------------------------------------ #
    def plot_density(self, features=None):
        """
        KDE density plots for continuous features by churn category.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()
            features = [f for f in features if f != self.target]

        n = len(features)
        fig, axes = plt.subplots(n, 1, figsize=(12, 4 * n))
        if n == 1:
            axes = [axes]

        for i, feature in enumerate(features):
            for cat in ['No Churn', 'Partial Churn', 'Full Churn']:
                subset = self.data[self.data[self.target] == cat][feature].dropna()
                if len(subset) > 1:
                    subset.plot.kde(ax=axes[i], label=cat, linewidth=2)
            axes[i].set_title(f'Density Plot: {feature}', fontsize=12, fontweight='bold')
            axes[i].set_xlabel(feature)
            axes[i].legend()

        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    #  Correlation Heatmap
    # ------------------------------------------------------------------ #
    def plot_correlation_heatmap(self, features=None):
        """
        Correlation heatmap of numeric features.
        """
        if features is None:
            features = self.data.select_dtypes(include=[np.number]).columns.tolist()

        corr_matrix = self.data[features].corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.3f',
                    cmap='RdBu_r', center=0, vmin=-1, vmax=1,
                    square=True, linewidths=0.5, ax=ax,
                    cbar_kws={"shrink": 0.8})
        ax.set_title('Correlation Heatmap (Numeric Features)',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

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

        plt.tight_layout()
        plt.show()

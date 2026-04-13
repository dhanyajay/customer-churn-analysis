import pandas as pd

class MergeData:
    def __init__(self, account_churn, retention_data, bob_data):
        self.account_churn = account_churn.copy()
        self.retention_data = retention_data.copy()
        self.bob_data = bob_data.copy()
        self.analysis_df = None

    def merge_and_prepare_data(self):
        """
        Merge retention and BoB data with churn categories for feature analysis
        """
        print("Merging and Preparing Data for Analysis...")

        # First, reset account_churn index to make account_number a column
        account_churn_reset = self.account_churn.reset_index()

        # Convert Account number in bob_data to string for consistent matching
        account_churn_reset['account_number'] = account_churn_reset['account_number'].astype(str)
        self.bob_data['account_number'] = self.bob_data['account_number'].astype(str)

        # Create account-level aggregates from retention data
        retention_cleaned_copy = self.retention_data.copy()
        retention_cleaned_copy['customer_account_number'] = retention_cleaned_copy['customer_account_number'].astype(str)

        # Check which columns exist
        print(f"Available retention columns: {retention_cleaned_copy.columns.tolist()}")

        # Aggregate retention data by account - only use columns that exist
        agg_cols = {}
        if 'customer_tier' in retention_cleaned_copy.columns:
            agg_cols['customer_tier'] = lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None
        if 'case_type' in retention_cleaned_copy.columns:
            agg_cols['case_type'] = lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None
        if 'pull_type' in retention_cleaned_copy.columns:
            agg_cols['pull_type'] = lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None
        if 'current_status' in retention_cleaned_copy.columns:
            agg_cols['current_status'] = lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None
        if 'resolution_status' in retention_cleaned_copy.columns:
            agg_cols['resolution_status'] = lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None
        if 'number_of_repair_cases' in retention_cleaned_copy.columns:
            agg_cols['number_of_repair_cases'] = 'sum'
        if 'country' in retention_cleaned_copy.columns:
            agg_cols['country'] = lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None

        retention_agg = retention_cleaned_copy.groupby('customer_account_number').agg(agg_cols).reset_index()
        retention_agg.columns = ['account_number'] + [f'retention_{col}' for col in retention_agg.columns[1:]]

        # Aggregate bob data by account
        bob_agg = self.bob_data.groupby('account_number').agg({
            'product_bob': lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None,
            'fee_bob': 'mean',
            'total_bob': 'sum',
            'renewal_type': lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None,
            'branch': lambda x: x.dropna().mode()[0] if len(x.dropna()) > 0 and len(x.dropna().mode()) > 0 else None,
        }).reset_index()

        bob_agg.columns = ['account_number', 'main_product_bob', 'avg_fee_bob', 'total_revenue_bob', 'renewal_type', 'branch_bob']

        # Merge all data
        self.analysis_df = account_churn_reset.merge(retention_agg, on='account_number', how='left')
        self.analysis_df = self.analysis_df.merge(bob_agg, on='account_number', how='left')

        print(f"Final analysis dataset shape: {self.analysis_df.shape}")
        print(f"Analysis dataset columns: {self.analysis_df.columns.tolist()}")

        return self.analysis_df
import pandas as pd

class MergeData:
    def __init__(self, retention_cleaned, bob_cleaned):
        self.retention_cleaned = retention_cleaned.copy()
        self.bob_cleaned = bob_cleaned.copy()
        self.merged_df = None

    def merge_data(self):
        print("Merging retention and BoB data...")

        # Ensure same datatype
        self.bob_cleaned['account_number'] = self.bob_cleaned['account_number'].astype(str)
        self.retention_cleaned['customer_account_number'] = self.retention_cleaned['customer_account_number'].astype(str)

        # Merge
        merged = pd.merge(
            self.bob_cleaned,
            self.retention_cleaned,
            left_on='account_number',
            right_on='customer_account_number',
            how='inner'
        )

        # Remove duplicate column
        if 'customer_account_number' in merged.columns:
            merged.drop(columns=['customer_account_number'], inplace=True)

        self.merged_df = merged

        print(f"Merged dataset shape: {self.merged_df.shape}")
        print(f"Columns: {self.merged_df.columns.tolist()}")

        return self.merged_df
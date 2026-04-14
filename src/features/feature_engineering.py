import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class FeatureEngineering:
    def __init__(self, data):
        self.data = data.copy()

    def engineer_features(self):
        print("Starting feature engineering process...")
        df = self.data
        
        # Handling missing values
        print("Handling missing values...")
        if 'unit_amount' in df.columns:
            df['unit_amount'].fillna(df['unit_amount'].median(), inplace=True)
        if 'msdyn_product_number' in df.columns:
            df['msdyn_product_number'].fillna('Unknown', inplace=True)
        if 'product_name' in df.columns:
            df['product_name'].fillna('Unknown', inplace=True)

        # Basic derived features
        # Assuming agreement_start_date is available and correctly formatted
        if 'agreement_start_date' in df.columns and 'agreement_end_date' in df.columns:
            print("Creating date-based features...")
            df['agreement_start_date'] = pd.to_datetime(df['agreement_start_date'], errors='coerce')
            df['agreement_end_date'] = pd.to_datetime(df['agreement_end_date'], errors='coerce')
            df['agreement_duration_days'] = (df['agreement_end_date'] - df['agreement_start_date']).dt.days

        # Ratio features
        if 'active_agreements' in df.columns and 'total_agreements' in df.columns:
            print("Creating agreement ratio feature...")
            df['active_ratio'] = df['active_agreements'] / df['total_agreements'].replace(0, np.nan)
            df['active_ratio'].fillna(0, inplace=True)

        # Scale continuous features
        print("Scaling continuous features...")
        scaler = StandardScaler()
        continuous_cols = [col for col in ['total_agreements', 'active_agreements', 'lost_agreements', 
                                         'avg_fee_bob', 'total_revenue_bob', 'agreement_duration_days', 'active_ratio'] if col in df.columns]
        if continuous_cols:
            scaled_features = scaler.fit_transform(df[continuous_cols])
            for i, col in enumerate(continuous_cols):
                df[f'{col}_scaled'] = scaled_features[:, i]

        print(f"Feature engineering complete. New shape: {df.shape}")
        return df

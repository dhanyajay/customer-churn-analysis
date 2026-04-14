import pandas as pd

class ChurnClassification:
    def __init__(self, merged_df):
        self.merged_df = merged_df.copy()
        self.churn_df = None

    def classify_churn(self):
        print("Performing churn classification...")

        df = self.merged_df

        # Total agreements
        total_agg = df.groupby('account_number')['agreement_number'].nunique().reset_index()
        total_agg.rename(columns={'agreement_number': 'total_agreements'}, inplace=True)

        # Active agreements
        active_agg = df[df['system_status'].str.lower() == 'active'] \
            .groupby('account_number')['agreement_number'].nunique().reset_index()
        active_agg.rename(columns={'agreement_number': 'active_agreements'}, inplace=True)

        # Lost agreements
        lost_status = ['Customer Lost', 'Converted to Cancellation']
        lost_cond = df['resolution_status'].isin(lost_status) | (df['system_status'].str.lower() == 'canceled')
        lost_agg = df[lost_cond] \
            .groupby('account_number')['agreement_number'].nunique().reset_index()
        lost_agg.rename(columns={'agreement_number': 'lost_agreements'}, inplace=True)

        # Combine
        final_df = total_agg.merge(active_agg, on='account_number', how='left') \
                            .merge(lost_agg, on='account_number', how='left')

        # Fill NaN
        final_df[['active_agreements', 'lost_agreements']] = final_df[
            ['active_agreements', 'lost_agreements']
        ].fillna(0).astype(int)

        # Churn Logic
        def classify(row):
            if row['lost_agreements'] == row['total_agreements']:
                return 'full_churn'
            elif row['lost_agreements'] > 0:
                return 'partial_churn'
            else:
                return 'no_churn'

        final_df['target'] = final_df.apply(classify, axis=1)

        self.churn_df = final_df

        print(f"Churn dataset shape: {self.churn_df.shape}")
        print(f"Columns: {self.churn_df.columns.tolist()}")

        return self.churn_df
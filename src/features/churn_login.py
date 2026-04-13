import pandas as pd
import numpy as np

def create_churn_labels(df):
    """
    Creates agreement-level and customer-level churn
    """

    # 1. Agreement churn
    df['agreement_churn'] = np.where(
        df['resolution_status'] == 'Customer Lost', 1, 0
    )

    # 2. Customer-level churn
    customer_churn = df.groupby('customer_account_number')['agreement_churn'].agg(
        total='count',
        lost='sum'
    ).reset_index()

    # 3. Final churn logic
    def assign_churn(row):
        if row['lost'] == row['total']:
            return 1   # full churn
        elif row['lost'] == 0:
            return 0   # no churn
        else:
            return 2   # partial churn

    customer_churn['customer_churn'] = customer_churn.apply(assign_churn, axis=1)

    return df, customer_churn
import pandas as pd
import numpy as np
def create_churn_labels(df):
    # Agreement-level churn
    df['agreement_churn'] = np.where(
        df['resolution_status'] == "Customer Lost", 1, 0
    )

    # Customer-level aggregation
    
    customer_churn = df.groupby('customer_account_number')['agreement_churn'].agg(
        total_agreements='count',
        lost_agreements='sum'
    ).reset_index()

    # Active agreements
    customer_churn['active_agreements'] = (
        customer_churn['total_agreements'] - customer_churn['lost_agreements']
    )
    # Customer-level churn classification
   
    conditions = [
        customer_churn['lost_agreements'] == customer_churn['total_agreements'],  # full churn
        customer_churn['lost_agreements'] == 0                                    # no churn
    ]

    choices = [1, 0]

    customer_churn['customer_churn'] = np.select(
        conditions,
        choices,
        default=2  # partial churn
    )

    return df, customer_churn
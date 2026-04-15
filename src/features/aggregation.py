import pandas as pd

def aggregate_bob_to_customer(df):

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Remove ID columns
    num_cols = [col for col in num_cols if col not in ['account_number', 'agreement_number']]
    cat_cols = [col for col in cat_cols if col not in ['account_number']]

    # NUMERICAL AGGREGATION
    
    agg_dict = {}

    for col in num_cols:

        if col == 'total_bob':
            agg_dict[col] = 'sum'

        elif col in ['unit_amount', 'service_interval', 'billing_interval']:
            agg_dict[col] = 'mean'

        else:
            agg_dict[col] = 'median'   # safe fallback

    # CATEGORICAL AGGREGATION (MODE)

    for col in cat_cols:
        agg_dict[col] = lambda x: x.mode()[0] if not x.mode().empty else "Unknown"

    # GROUPBY

    agg_df = df.groupby('account_number').agg(agg_dict).reset_index()

    # ADD IMPORTANT FEATURES

    agg_df['total_agreements'] = df.groupby('account_number')['agreement_number'].nunique().values
    agg_df = agg_df.rename(columns={
    'total_bob': 'total_revenue',
    'unit_amount': 'avg_unit_amount'
})
    return agg_df
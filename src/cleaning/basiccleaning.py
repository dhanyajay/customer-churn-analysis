def basic_cleaning(df):

    # Drop rows with null account_number 
    if "account_number" in df.columns:
        df = df.dropna(subset=["account_number"])
 
    if "customer_account_number" in df.columns:
        df = df.dropna(subset=["customer_account_number"])
 
    # 3. Remove duplicates 
    df = df.drop_duplicates()
 
    return df

def clean_cols(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df
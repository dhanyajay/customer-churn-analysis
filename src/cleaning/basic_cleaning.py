def standardize_column_names(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w\s]", "", regex=True)  # remove special chars
        .str.replace(" ", "_")
    )

    return df

def basic_cleaning(df):
    # 1. Standardize column names
    df = standardize_column_names(df)

    # 2. Drop null keys
    if "account_number" in df.columns:
        df = df.dropna(subset=["account_number"])

    if "customer_account_number" in df.columns:
        df = df.dropna(subset=["customer_account_number"])

    # 3. Remove duplicates
    if "agreement_number" in df.columns and "account_number" in df.columns:
        df = df.drop_duplicates(subset=["account_number", "agreement_number"])

    else:
        # For other datasets
        df = df.drop_duplicates()

    return df
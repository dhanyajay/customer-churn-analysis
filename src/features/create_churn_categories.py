import pandas as pd

class CreateChurnCategories:
    def __init__(self, bob_data):
        self.bob_data = bob_data.copy()
        self.account_churn = None

    def create_churn_categories(self):
        """
        Create 3-level churn classification:
        - No Churn: Customer maintains all active agreements
        - Partial Churn: Customer loses some agreements but maintains some
        - Full Churn: Customer loses all agreements
        """
        print("Creating Churn Categories...")

        # Analyze agreement-level churn from BoB data
        self.bob_data['agreement_end_date_dt'] = pd.to_datetime(self.bob_data['agreement_end_date'], errors='coerce')
        today = pd.Timestamp.now()

        # Agreement is considered "lost" if:
        # 1. system_status is Canceled, Expired, or Estimate
        # 2. OR if system_status is Active but end_date has passed
        def determine_agreement_status(row):
            status = row['system_status']
            end_date = row['agreement_end_date_dt']

            # If status is explicitly Canceled, Expired, or Estimate -> Lost
            if status in ['Canceled', 'Expired', 'Estimate']:
                return 'lost'
            # If Active but end date has passed -> Lost
            elif status == 'Active' and pd.notna(end_date) and end_date < today:
                return 'lost'
            # Otherwise -> Active
            else:
                return 'active'

        self.bob_data['agreement_status'] = self.bob_data.apply(determine_agreement_status, axis=1)

        # Aggregate at account level
        self.account_churn = self.bob_data.groupby('account_number').agg({
            'agreement_number': 'count',  # total_agreements
            'agreement_status': lambda x: (x == 'active').sum(),  # active_agreements
        }).rename(columns={'agreement_number': 'total_agreements', 'agreement_status': 'active_agreements'})

        self.account_churn['lost_agreements'] = self.account_churn['total_agreements'] - self.account_churn['active_agreements']

        # Define churn categories
        def categorize_churn(row):
            if row['lost_agreements'] == 0:
                return 'No Churn'
            elif row['lost_agreements'] == row['total_agreements']:
                return 'Full Churn'
            else:
                return 'Partial Churn'

        self.account_churn['churn_category'] = self.account_churn.apply(categorize_churn, axis=1)

        print(f"Account-level churn aggregation created!")
        print(f"Total unique accounts: {len(self.account_churn)}")
        print(f"Churn distribution:\n{self.account_churn['churn_category'].value_counts()}")
        print(f"Churn categories breakdown (%):\n{self.account_churn['churn_category'].value_counts(normalize=True) * 100}")

        return self.account_churn
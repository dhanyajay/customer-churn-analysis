class StoreData:
    def __init__(self, retention, bob, target):
        self.retention = retention
        self.bob = bob
        self.target = target

    def save_data(self):
        self.retention.to_csv("../../data/02_intermediate/cleaned_retention.csv", index=False)
        self.bob.to_csv("../../data/02_intermediate/cleaned_bob.csv", index=False)
        self.target.to_csv("../../data/02_intermediate/target_y.csv", index=False)
        print("Data saved successfully to the intermediate data folder!")
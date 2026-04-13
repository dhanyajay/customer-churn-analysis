import re

class CleanData:
    def __init__(self, retention, bob):
        # Load the data using the LoadData class
        self.retention = retention
        self.bob = bob
        print("Data loaded successfully in CleanData class!")
    
    def columns_to_snake_case(self, df):
        """
        Convert all column names in a DataFrame to snake_case.
        Args:
            df: pandas DataFrame
        Returns:
            DataFrame with snake_case column names
        """
        def convert_name(name):
            # Convert column names to snake_case
            # 1. Handle camelCase: Replace CamelCase with camel_case
            s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
            # 2. Handle CamelCase/Upper: Replace 2 or more caps together
            s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
            # 3. Replace spaces, hyphens, and other non-alphanumeric with underscores
            s3 = re.sub(r'[^a-zA-Z0-9]+', '_', s2)
            # 4. Lowercase and strip trailing underscores
            return s3.lower().strip('_')

        df.columns = [convert_name(col) for col in df.columns]
        return df
    
    def dropping_duplicates(self, df):
        """
        Drop duplicate rows from a DataFrame.
        Args:
            df: pandas DataFrame
        Returns:
            DataFrame with duplicate rows dropped
        """
        return df.drop_duplicates()
    
    def dropping_nulls(self, df):
        """
        Drop rows with null values from a DataFrame.
        Args:
            df: pandas DataFrame
        Returns:
            DataFrame with rows containing null values dropped
        """        
        return df.dropna()
    
    def filling_with_modes(self, df):
        """
        Fill null values in a DataFrame with the mode of each column.
        Args:
            df: pandas DataFrame
        Returns:
            DataFrame with null values filled with modes
        """
        for column in df.columns:
            mode_values = df[column].mode()  # Get the mode value for the column
            if len(mode_values) > 0:
                mode_value = mode_values[0]
                df[column].fillna(mode_value, inplace=True)  # Fill nulls with the mode value
        return df
    
    def filling_with_means(self, df):
        """
        Fill null values in a DataFrame with the mean of each column.
        Args:
            df: pandas DataFrame
        Returns:
            DataFrame with null values filled with means
        """
        for column in df.columns:
            if df[column].dtype in ['float64', 'int64']:  # Only fill numeric columns with mean
                mean_value = df[column].mean()  # Get the mean value for the column
                df[column].fillna(mean_value, inplace=True)  # Fill nulls with the mean value
        return df
    
    def filling_with_medians(self, df):
        """
        Fill null values in a DataFrame with the median of each column.
        Args:
            df: pandas DataFrame
        Returns:
            DataFrame with null values filled with medians
        """
        for column in df.columns:
            if df[column].dtype in ['float64', 'int64']:  # Only fill numeric columns with median
                median_value = df[column].median()  # Get the median value for the column
                df[column].fillna(median_value, inplace=True)  # Fill nulls with the median value
        return df
    
    def clean_data_with_modes(self):
        """
        Clean the retention and bob DataFrames by applying the following steps:
        1. Convert column names to snake_case
        2. Drop duplicate rows
        3. Drop rows with null values
        4. Fill null values with modes
        """
        self.retention = self.columns_to_snake_case(self.retention)
        self.retention = self.dropping_duplicates(self.retention)
        self.retention = self.filling_with_modes(self.retention)

        self.bob = self.columns_to_snake_case(self.bob)
        self.bob = self.dropping_duplicates(self.bob)
        self.bob = self.filling_with_modes(self.bob)

        print("Data cleaning completed successfully!")
        return self.retention, self.bob
    
    def clean_data_with_means(self):
        """
        Clean the retention and bob DataFrames by applying the following steps:
        1. Convert column names to snake_case
        2. Drop duplicate rows
        3. Drop rows with null values
        4. Fill null values with means
        """
        self.retention = self.columns_to_snake_case(self.retention)
        self.retention = self.dropping_duplicates(self.retention)
        self.retention = self.filling_with_means(self.retention)

        self.bob = self.columns_to_snake_case(self.bob)
        self.bob = self.dropping_duplicates(self.bob)
        self.bob = self.filling_with_means(self.bob)

        print("Data cleaning completed successfully!")
        return self.retention, self.bob
    
    def clean_data_with_medians(self):
        """
        Clean the retention and bob DataFrames by applying the following steps:
        1. Convert column names to snake_case
        2. Drop duplicate rows
        3. Drop rows with null values
        4. Fill null values with medians
        """
        self.retention = self.columns_to_snake_case(self.retention)
        self.retention = self.dropping_duplicates(self.retention)
        self.retention = self.filling_with_medians(self.retention)

        self.bob = self.columns_to_snake_case(self.bob)
        self.bob = self.dropping_duplicates(self.bob)
        self.bob = self.filling_with_medians(self.bob)

        print("Data cleaning completed successfully!")
        return self.retention, self.bob
    
    def clean_data_with_dropping_nulls(self):
        """
        Clean the retention and bob DataFrames by applying the following steps:
        1. Convert column names to snake_case
        2. Drop duplicate rows
        3. Drop rows with null values
        """
        self.retention = self.columns_to_snake_case(self.retention)
        self.retention = self.dropping_duplicates(self.retention)
        self.retention = self.dropping_nulls(self.retention)

        self.bob = self.columns_to_snake_case(self.bob)
        self.bob = self.dropping_duplicates(self.bob)
        self.bob = self.dropping_nulls(self.bob)

        print("Data cleaning completed successfully!")
        return self.retention, self.bob
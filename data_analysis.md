# Customer Churn Analysis Data Documentation

## Overview
This document analyzes the two CSV files (`Retention.csv` and `bob.csv`) for customer churn analysis. Both files contain data related to customer agreements and retention efforts for a business dealing with machine services, chemistry, and waste management.

## Data Sources

### 1. Retention.csv
- **Purpose**: Contains retention cases for customers at risk of churning
- **Key Columns**:
  - `Case ID`: Unique identifier for each retention case
  - `Case Title`: Description of the case (e.g., "Service Claim", "SRF - Machine not used", "Competition seen on site")
  - `Country`: Customer location
  - `Pull VAN`, `New VAN`, `VAN`: Financial values related to the agreement (VAN likely stands for Value Added something)
  - `Number of Contracts`: Number of contracts per customer
  - `Machines`: Number of machines
  - `Branch`: Business branch location
  - `Customer Account Number`: Customer identifier (appears empty in sample data)
  - `Customer Name`: Customer name
  - `Customer Since`: Customer tenure start date
  - `Agreement End Date`: When the agreement ends
  - `Pull Type`: Type of pull (all "Full" in sample)
  - `Case Type`: Type of retention case
  - `Risk`: Risk level (all "Risk" in sample)
  - `Current Status`: Case status (all "In Progress" in sample)
  - `Resolution Status`: Resolution status (all "OPEN - In Progress" in sample)
  - `Number Of Repair Cases`: Number of repair incidents
  - `Number of OverdueServices`: Number of overdue services
  - `CompanySize`: Size category of the company
  - `Customer Tier`: Customer tier level
  - `Case Origin`: How the case was created
  - `Case Creation Date`: When the case was created
  - `Resolved Time`, `Registered Time`: Time-related fields
  - `Resolved Date`, `Registered Date`: Date fields
  - `Expected Pull Date`: Expected date of equipment pull

### 2. bob.csv
- **Purpose**: Detailed customer agreement and billing data
- **Key Columns**:
  - `account_number`: Unique customer account identifier
  - `company_sizing`: Company size category (e.g., ">1000", "20-49", "50-99")
  - `postal_code`: Customer postal code
  - `branch`: Business branch
  - `vat_number`: VAT number
  - `agreement_number`: Unique agreement identifier
  - `agreement_start_date`: Agreement start date
  - `agreement_end_date`: Agreement end date
  - `renewal_type`: Renewal type (e.g., "Automatic Renewal")
  - `agreement_type`: Type of agreement (e.g., "Scheduled Billing")
  - `line_of_business`: Business line (e.g., "Machine Services", "Auto waste", "Chemistry")
  - `system_status`: System status (e.g., "Active")
  - `product_bob`, `fee_bob`, `total_bob`: Financial values (BOB likely stands for Bill of Materials or similar)
  - `is_bob`: Boolean indicator
  - `bpg`: Business Process Group
  - `msdyn_product_number`: Product number
  - `product_name`: Product description
  - `service_interval`: Service frequency
  - `unit_amount`: Unit pricing
  - `billing_interval`: Billing frequency
  - `billing_period`: Billing period
  - `machine`: Machine type
  - `machine_variant`: Machine variant
  - `chemistry`: Chemistry type

## Usability for Churn Analysis

### Suitable for Churn Analysis
- **Both files**: Can be used together for comprehensive churn analysis
- **Retention.csv**: Represents customers currently in retention processes (at risk of churning)
- **bob.csv**: Provides detailed customer profile and agreement data for all customers

### Potential Target Variable
- **Derived Target**: Churn can be determined by:
  - If `agreement_end_date` < current date and no renewal occurred
  - Presence of a retention case in Retention.csv (indicates churn risk)
  - If `Pull VAN` > 0 (indicates value being pulled/churned)
  - Case resolution status (if resolved as churned vs retained)

### Feature Variables (Input Columns)
From **bob.csv**:
- `company_sizing`: Company size (categorical)
- `postal_code`: Location data
- `branch`: Branch location
- `agreement_start_date`: Tenure calculation
- `agreement_end_date`: Agreement duration
- `renewal_type`: Renewal preference
- `agreement_type`: Agreement structure
- `line_of_business`: Business segment
- `total_bob`: Total agreement value
- `product_name`: Product details
- `service_interval`: Service frequency
- `unit_amount`: Pricing tier
- `billing_interval`: Billing frequency
- `machine`: Equipment type
- `machine_variant`: Equipment variant
- `chemistry`: Chemical type

From **Retention.csv**:
- `Number of Contracts`: Contract count
- `Machines`: Equipment count
- `CompanySize`: Company size
- `Customer Tier`: Customer segmentation
- `Number Of Repair Cases`: Service history
- `Number of OverdueServices`: Service quality indicator
- `Case Type`: Reason for retention case
- `Case Origin`: How the issue arose

## Data Quality Notes
- Retention.csv has some empty fields (Customer Account Number)
- Dates are in various formats (DD-MM-YYYY and YYYY-MM-DD)
- Financial values appear consistent
- bob.csv is large (>50MB), indicating substantial customer base
- Both files use UK-based data (United Kingdom, postal codes)

## Recommended Analysis Approach
1. Merge datasets on customer identifiers (account_number, customer name)
2. Create target variable based on churn criteria
3. Feature engineering: Calculate tenure, total value, service metrics
4. Handle categorical variables appropriately
5. Consider temporal aspects (agreement dates, case creation dates)
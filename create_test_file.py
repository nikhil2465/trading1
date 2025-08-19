import pandas as pd
import numpy as np

# Create sample data
data = {
    'Symbol': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ITC', 'BHARTIARTL', 'SBIN', 'BAJFINANCE', 'LT'],
    'Expiry': ['25-AUG-2023'] * 10,
    'Strike Price': [2500, 3500, 1500, 1500, 2400, 450, 800, 600, 7000, 2500],
    'Option Type': ['CE', 'PE', 'CE', 'PE', 'CE', 'PE', 'CE', 'PE', 'CE', 'PE'],
    'LTP': [45.25, 78.50, 120.75, 65.30, 95.20, 12.80, 34.60, 23.45, 560.75, 87.90],
    'Open Interest': [12500, 7800, 15600, 9200, 11400, 5600, 8700, 10200, 4500, 6800],
    'PCR Sum': [2.5, 1.8, 3.2, 2.1, 4.5, 1.2, 2.8, 3.5, 1.9, 2.4],
    'CPR Sum': [1.8, 2.3, 1.5, 2.8, 1.2, 3.5, 2.1, 1.7, 2.9, 2.0],
    'Volume': [4500, 3200, 5600, 2800, 3900, 2100, 3400, 4100, 1800, 2900],
    'PCR OI': [1.8, 2.1, 2.8, 1.9, 3.5, 1.5, 2.4, 3.1, 2.2, 1.7],
    'PCR Volume': [1.5, 1.9, 2.5, 1.7, 3.2, 1.3, 2.1, 2.8, 2.0, 1.5],
    'PCR Change in OI': [0.8, 1.2, 1.8, 0.9, 2.5, 0.7, 1.5, 2.1, 1.3, 0.9],
    'CPR OI': [1.2, 1.5, 2.1, 1.3, 2.8, 1.1, 1.9, 2.5, 1.7, 1.2],
    'CPR Vol': [1.0, 1.3, 1.8, 1.1, 2.4, 0.9, 1.6, 2.2, 1.5, 1.0],
    'Resistance': [2550, 3450, 1550, 1480, 2450, 440, 820, 590, 7050, 2480],
    'PCR Support': ['Support', 'Good Support', 'Very Good Support', 'Support', 'Very Good Support', 
                   'Support', 'Good Support', 'Very Good Support', 'Support', 'Good Support']
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_path = 'macro_processed_sample.xlsx'
df.to_excel(output_path, index=False, sheet_name='Processed Data')
print(f"Sample test file created: {output_path}")
print("Please upload this file using the 'Process After Macro' form on the Tools page.")

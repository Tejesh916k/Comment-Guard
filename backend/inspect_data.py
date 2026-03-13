import pandas as pd
import sys

with open('inspect_out.txt', 'w', encoding='utf-8') as f:
    f.write("Loading dataset...\n")
    try:
        df = pd.read_excel('data/training_data_telugu-hate.xlsx')
        f.write("Columns: " + str(df.columns.tolist()) + "\n")
        f.write("Shape: " + str(df.shape) + "\n")
        if 'label' in df.columns:
            f.write("Value Counts for 'label':\n" + str(df['label'].value_counts()) + "\n")
        f.write("\nFirst 5 rows:\n")
        f.write(str(df.head()) + "\n")
        
        # Look for missing values
        f.write("\nMissing Values:\n" + str(df.isnull().sum()) + "\n")
    except Exception as e:
        f.write("Error: " + str(e) + "\n")

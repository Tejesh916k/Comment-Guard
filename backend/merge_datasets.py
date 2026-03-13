import pandas as pd
from pathlib import Path

def merge_datasets():
    data_dir = Path("data")
    custom_words_file = data_dir / "custom_badwords_dataset.xlsx"
    main_dataset_file = data_dir / "training_data_telugu-hate.xlsx"
    
    if not custom_words_file.exists():
        print(f"Error: {custom_words_file} not found.")
        return
        
    if not main_dataset_file.exists():
        print(f"Error: {main_dataset_file} not found.")
        return

    # Load both datasets
    print("Loading data...")
    custom_df = pd.read_excel(custom_words_file)
    main_df = pd.read_excel(main_dataset_file)
    
    print(f"Original main dataset size: {len(main_df)}")
    print(f"Custom badwords size: {len(custom_df)}")
    
    # Identify column names in main_dataset (usually text/comment and label/category)
    # Based on kaggle_model script, we know text could be 'text' or 'comment'
    text_col_main = next((c for c in main_df.columns if str(c).lower() in ['text', 'comment', 'comments', 'sentence']), 'text')
    label_col_main = next((c for c in main_df.columns if str(c).lower() in ['label', 'labels', 'category', 'class']), 'label')
    
    print(f"Identified columns in main dataset -> Text: '{text_col_main}', Label: '{label_col_main}'")
    
    # Rename custom dataset columns to match main dataset
    custom_df = custom_df.rename(columns={'text': text_col_main, 'label': label_col_main})
    
    # Combine the dataframes
    merged_df = pd.concat([main_df, custom_df], ignore_index=True)
    
    # Remove any absolute duplicates just in case
    merged_df = merged_df.drop_duplicates(subset=[text_col_main]).reset_index(drop=True)
    
    print(f"New merged dataset size: {len(merged_df)}")
    
    # Make a backup of the original just in case we need it
    backup_path = data_dir / "training_data_telugu-hate_backup2.xlsx"
    main_df.to_excel(backup_path, index=False)
    print(f"Saved backup of original to {backup_path}")
    
    # Overwrite the main dataset
    merged_df.to_excel(main_dataset_file, index=False)
    print(f"Successfully merged and saved updated dataset to {main_dataset_file}")

if __name__ == "__main__":
    merge_datasets()

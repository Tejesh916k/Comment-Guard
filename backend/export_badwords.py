import os
import base64
import pandas as pd
from pathlib import Path

def export_badwords_to_excel(output_filename="custom_badwords_dataset.xlsx"):
    data_dir = Path("data")
    toxic_words = []

    # 1. Load regular badwords
    p1 = data_dir / "telugu_badwords.txt"
    if p1.exists():
        with open(p1, "r", encoding="utf-8") as f:
            toxic_words.extend([l.strip() for l in f if l.strip()])
            
    # 2. Load secure base64 badwords
    p2 = data_dir / "secure_words.bin"
    if p2.exists():
        with open(p2, "rb") as f:
            decoded = base64.b64decode(f.read()).decode("utf-8")
            toxic_words.extend([l.strip() for l in decoded.splitlines() if l.strip()])
            
    # 3. Load bad emojis
    p3 = data_dir / "bad_emojis.txt"
    if p3.exists():
        with open(p3, "r", encoding="utf-8") as f:
            toxic_words.extend([l.strip() for l in f if l.strip() and not l.strip().startswith("#")])
            
    # Remove duplicates
    toxic_words = list(set(toxic_words))
    print(f"Total unique offensive terms gathered: {len(toxic_words)}")
    
    if not toxic_words:
        print("No words found to export.")
        return
        
    # Create a DataFrame
    # Here we are just exporting the raw words as 'toxic'
    df = pd.DataFrame({
        'text': toxic_words,
        'label': 'toxic'
    })
    
    # Save to Excel
    output_path = data_dir / output_filename
    df.to_excel(output_path, index=False)
    print(f"Successfully exported {len(toxic_words)} words to {output_path}")

if __name__ == "__main__":
    export_badwords_to_excel()

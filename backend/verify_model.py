"""
MODEL VERIFICATION SCRIPT
Use this to test your trained model locally on your PC.
"""

import os
from transformers import pipeline

def test_model():
    # 1. Path to your model folder
    # Change this to 'model_output_v2' if testing the new version
    model_path = "./model_output" 
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model folder '{model_path}' not found.")
        print("Please ensure you have moved your Kaggle/Colab output into the 'backend' folder.")
        return

    print("🔄 Loading model (this may take a few seconds)...")
    try:
        # Load the toxicity classifier
        classifier = pipeline(
            "text-classification", 
            model=model_path, 
            tokenizer=model_path,
            device=-1 # Use -1 for CPU, 0 for first GPU
        )
        print("✅ Model loaded successfully!\n")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    print("Enter 'quit' to exit.")
    while True:
        text = input("\n📝 Enter a comment to test: ")
        if text.lower() == 'quit':
            break
        
        if not text.strip():
            continue

        # Get prediction
        result = classifier(text)[0]
        
        label = result['label']
        score = result['score']

        # Map labels to human-readable text
        # LABEL_1 is usually Toxic, LABEL_0 is Safe
        is_toxic = "TOXIC 🔴" if label == "LABEL_1" else "SAFE 🟢"
        
        print("-" * 30)
        print(f"Result: {is_toxic}")
        print(f"Confidence: {score*100:.2f}%")
        print("-" * 30)

if __name__ == "__main__":
    test_model()

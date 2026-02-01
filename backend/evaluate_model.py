"""
Evaluation Script for AI Comment Moderation System

This script evaluates the performance of the comment moderation system by:
- Loading a labeled test dataset
- Running predictions through the moderation API (using TestClient for direct local testing)
- Calculating precision, recall, F1 score, accuracy
- Generating confusion matrix
- Tracking false positives and false negatives
"""

import json
import sys
import os
from typing import List, Dict, Tuple
from collections import defaultdict
from fastapi.testclient import TestClient

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app

# Try to import sklearn
try:
    from sklearn.metrics import (
        precision_score, 
        recall_score, 
        f1_score, 
        accuracy_score,
        confusion_matrix,
        classification_report
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Warning: scikit-learn not installed. Using manual calculations.")
    SKLEARN_AVAILABLE = False


class ModelEvaluator:
    """Evaluates the comment moderation model performance"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.results = defaultdict(list)
        
    def load_test_data(self, filepath: str) -> List[Dict]:
        """Load test dataset from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded {len(data)} test cases from {filepath}")
            return data
        except FileNotFoundError:
            print(f"✗ Error: Test dataset not found at {filepath}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON in test dataset: {e}")
            sys.exit(1)
    
    def predict(self, text: str, strictness: str = "high") -> Tuple[bool, Dict]:
        """
        Get prediction from the moderation API using TestClient
        """
        try:
            response = self.client.post(
                "/analyze",
                json={"text": text, "strictness": strictness}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("is_toxic", False), data
            else:
                print(f"✗ API Error ({response.status_code}): {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"✗ Prediction error: {e}")
            return False, {}
    
    def evaluate(self, test_data: List[Dict], strictness: str = "high") -> Dict:
        """
        Evaluate model on test dataset
        """
        y_true = []
        y_pred = []
        false_positives = []
        false_negatives = []
        
        print(f"\n{'='*60}")
        print(f"Evaluating with strictness: {strictness.upper()}")
        print(f"{'='*60}\n")
        
        for i, case in enumerate(test_data, 1):
            text = case['text']
            ground_truth = case['ground_truth']
            category = case.get('category', 'unknown')
            
            # Convert ground truth to binary (1 = toxic, 0 = non-toxic)
            true_label = 1 if ground_truth == "toxic" else 0
            
            # Get prediction
            is_toxic, response = self.predict(text, strictness)
            pred_label = 1 if is_toxic else 0
            
            y_true.append(true_label)
            y_pred.append(pred_label)
            
            # Track errors
            if pred_label == 1 and true_label == 0:
                false_positives.append({
                    'text': text,
                    'category': category,
                    'response': response
                })
            elif pred_label == 0 and true_label == 1:
                false_negatives.append({
                    'text': text,
                    'category': category,
                    'response': response
                })
            
            if i % 50 == 0:
                print(f"Processed {i}/{len(test_data)} cases...")
        
        print(f"✓ Completed all {len(test_data)} predictions\n")
        
        # Calculate metrics
        if SKLEARN_AVAILABLE:
            metrics = {
                'strictness': strictness,
                'total_cases': len(test_data),
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1_score': f1_score(y_true, y_pred, zero_division=0),
                'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
                'false_positives': len(false_positives),
                'false_negatives': len(false_negatives),
                'false_positive_examples': false_positives,
                'false_negative_examples': false_negatives,
                'classification_report': classification_report(
                    y_true, y_pred, 
                    target_names=['Non-Toxic', 'Toxic'],
                    zero_division=0
                )
            }
        else:
            tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
            tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
            fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
            fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
            
            accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics = {
                'strictness': strictness,
                'total_cases': len(test_data),
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': [[tn, fp], [fn, tp]],
                'false_positives': len(false_positives),
                'false_negatives': len(false_negatives),
                'false_positive_examples': false_positives,
                'false_negative_examples': false_negatives,
            }
        
        return metrics
    
    def print_metrics(self, metrics: Dict):
        """Print metrics in a formatted way"""
        print(f"\n{'='*60}")
        print(f"EVALUATION RESULTS - Strictness: {metrics['strictness'].upper()}")
        print(f"{'='*60}\n")
        
        print(f"📊 Overall Metrics:")
        print(f"  Total Test Cases: {metrics['total_cases']}")
        print(f"  Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"  Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        print(f"  Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        print(f"  F1 Score:  {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
        
        print(f"\n⚠️  Error Analysis:")
        print(f"  False Positives: {metrics['false_positives']} (non-toxic flagged as toxic)")
        print(f"  False Negatives: {metrics['false_negatives']} (toxic not flagged)")
        
        if metrics['false_positive_examples']:
            print(f"\n  Top False Positive Examples:")
            for i, fp in enumerate(metrics['false_positive_examples'][:5], 1):
                print(f"    {i}. \"{fp['text']}\" (category: {fp['category']})")
                
        if metrics['false_negative_examples']:
            print(f"\n  Top False Negative Examples:")
            for i, fn in enumerate(metrics['false_negative_examples'][:5], 1):
                print(f"    {i}. \"{fn['text']}\" (category: {fn['category']})")

def main():
    print("\n" + "="*60)
    print("AI COMMENT MODERATION - MODEL EVALUATION (TestClient Mode)")
    print("="*60)
    
    evaluator = ModelEvaluator()
    data_path = os.path.join(os.path.dirname(__file__), "data", "test_dataset.json")
    test_data = evaluator.load_test_data(data_path)
    
    # Evaluate with HIGH strictness
    print("\n🔍 Running evaluation with HIGH strictness...")
    metrics_high = evaluator.evaluate(test_data, strictness="high")
    evaluator.print_metrics(metrics_high)
    
    # Evaluate with LOW strictness
    print("\n🔍 Running evaluation with LOW strictness...")
    metrics_low = evaluator.evaluate(test_data, strictness="low")
    evaluator.print_metrics(metrics_low)
    
    print("\n✅ Evaluation complete!")

if __name__ == "__main__":
    main()

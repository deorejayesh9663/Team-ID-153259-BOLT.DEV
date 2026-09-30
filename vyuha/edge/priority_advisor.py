import os
import sys
import numpy as np
import random
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
models_dir = os.path.join(os.path.dirname(parent_dir), "models")
os.makedirs(models_dir, exist_ok=True)

def generate_synthetic_data(num_samples=2000):
    X = []
    y = []
    for _ in range(num_samples):
        payload_weight = random.uniform(0.0, 100.0)
        deadline_urgency = random.uniform(0.0, 1.0)
        
        # Determine priority (1-5)
        # Heavy payload + Urgent deadline = High priority (1)
        # Light payload + Loose deadline = Low priority (5)
        # For simplicity, calculate a continuous score and bin it
        score = (payload_weight / 100.0) * 0.4 + deadline_urgency * 0.6
        
        if score > 0.8:
            priority = 1
        elif score > 0.6:
            priority = 2
        elif score > 0.4:
            priority = 3
        elif score > 0.2:
            priority = 4
        else:
            priority = 5
            
        # Add some noise
        if random.random() < 0.1:
            priority = max(1, min(5, priority + random.choice([-1, 1])))
            
        X.append([payload_weight, deadline_urgency])
        y.append(priority)
        
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)

def train_and_export():
    print("Generating synthetic data for Priority Advisor...")
    X, y = generate_synthetic_data()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Decision Tree Classifier (max_depth=5)...")
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Validation Accuracy: {acc * 100:.2f}%")
    
    print("Exporting model to ONNX...")
    initial_type = [('float_input', FloatTensorType([None, 2]))]
    onx = convert_sklearn(clf, initial_types=initial_type)
    
    onnx_path = os.path.join(models_dir, "priority_tree.onnx")
    with open(onnx_path, "wb") as f:
        f.write(onx.SerializeToString())
        
    print(f"✅ Successfully exported ONNX model to {onnx_path}")

if __name__ == "__main__":
    train_and_export()

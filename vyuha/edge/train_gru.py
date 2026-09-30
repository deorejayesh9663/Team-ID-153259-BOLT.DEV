import os
import sys
import json

# Fix Windows console encoding for PyTorch checkmarks
sys.stdout.reconfigure(encoding='utf-8')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

class CongestionGRU(nn.Module):
    def __init__(self, input_size=1, hidden_size=16, num_layers=1, output_size=1):
        super(CongestionGRU, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        out, _ = self.gru(x)
        # We just want the last time step
        out = out[:, -1, :]
        out = self.fc(out)
        return out

def train_and_export():
    data_file = os.path.join(current_dir, "data", "congestion_data.json")
    
    with open(data_file, 'r') as f:
        raw_data = json.load(f)
        
    features = []
    targets = []
    
    for item in raw_data:
        features.append(item["features"])
        targets.append([item["wait_time"]])
        
    # Convert to tensors
    # Shape: (batch, seq_len, input_size)
    X = torch.tensor(features, dtype=torch.float32).unsqueeze(-1)
    y = torch.tensor(targets, dtype=torch.float32)
    
    # 80/20 train/val split
    train_size = int(0.8 * len(X))
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size:], y[train_size:]
    
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    model = CongestionGRU()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    print("Training Congestion GRU...")
    epochs = 20
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        avg_loss = total_loss / len(train_loader)
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs, y_val).item()
            
        print(f"Epoch [{epoch+1}/{epochs}], Train Loss: {avg_loss:.4f}, Val Loss: {val_loss:.4f}")
        
    # Export to ONNX
    models_dir = os.path.join(os.path.dirname(parent_dir), "models")
    os.makedirs(models_dir, exist_ok=True)
    onnx_path = os.path.join(models_dir, "congestion_gru.onnx")
    
    # Create a dummy input for tracing
    dummy_input = torch.randn(1, 5, 1)
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        export_params=True, 
        opset_version=11, 
        do_constant_folding=True, 
        input_names=['input'], 
        output_names=['output'], 
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    print(f"Successfully exported ONNX model to {onnx_path}")
    print(f"Final Validation Loss: {val_loss:.4f} (Must be < 1.0)")
    
if __name__ == "__main__":
    train_and_export()

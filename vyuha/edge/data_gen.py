import os
import json
import random

def generate_training_data(num_samples=5000, output_file="data/congestion_data.json"):
    """
    Generates synthetic training data for the Congestion GRU.
    Features: sequence of 5 timesteps representing regional robot density (0.0 to 1.0).
    Label: wait_time (seconds), correlated with high density.
    """
    # Create dir relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, "congestion_data.json")
    
    data = []
    for _ in range(num_samples):
        # Generate a random sequence of 5 densities
        base_density = random.random()
        
        # Random walk for the sequence
        sequence = []
        current_density = base_density
        for _ in range(5):
            current_density = max(0.0, min(1.0, current_density + random.uniform(-0.1, 0.1)))
            sequence.append(round(current_density, 3))
            
        # The wait time is highly correlated with the average density
        avg_density = sum(sequence) / len(sequence)
        
        # Non-linear wait time mapping: higher density = exponentially worse wait time
        wait_time = max(0.0, (avg_density ** 2) * 10.0 + random.uniform(-0.5, 1.5))
        
        data.append({
            "features": sequence,
            "wait_time": round(wait_time, 2)
        })
        
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully generated {num_samples} samples at {file_path}")

if __name__ == "__main__":
    print("Generating Congestion GRU synthetic training data...")
    generate_training_data(10000)

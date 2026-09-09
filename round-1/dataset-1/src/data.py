#!/usr/bin/env python3
"""
Load the generated cache trace datasets and standardize to exp_sel_data_out.json schema.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def load_regime_split(regime: str, split: str) -> Dict[str, Any]:
    """Load a single split file for a regime."""
    file_path = Path(f"temp/datasets/{regime}_{split}.json")
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def main():
    """Main function to standardize datasets."""
    regimes = ["stationary_hot_clusters", "sudden_popularity_shift", "cold_start"]
    splits = ["train", "validation", "test"]
    
    output = {"datasets": []}
    
    for regime in regimes:
        all_examples = []
        for split in splits:
            split_data = load_regime_split(regime, split)
            # Assign metadata_fold: train->0, validation->1, test->2
            fold_map = {"train": 0, "validation": 1, "test": 2}
            metadata_fold = fold_map[split]
            
            for item in split_data["items"]:
                # Prepare input as JSON string of selected features
                input_features = {
                    "embedding": item["embedding"],
                    "popularity_count": item["popularity_count"],
                    "cluster_id": item["cluster_id"],
                    "timestamp": item["timestamp"],
                    "image_file": item["image_file"]
                }
                input_str = json.dumps(input_features)
                
                # Output is the item_id as string
                output_str = str(item["item_id"])
                
                example = {
                    "input": input_str,
                    "output": output_str,
                    "metadata_fold": metadata_fold,
                    "metadata_feature_names": list(input_features.keys())
                }
                all_examples.append(example)
        
        dataset_group = {
            "dataset": regime,
            "examples": all_examples
        }
        output["datasets"].append(dataset_group)
    
    # Write to full_data_out.json
    output_path = Path("full_data_out.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved standardized data to {output_path}")

if __name__ == "__main__":
    main()
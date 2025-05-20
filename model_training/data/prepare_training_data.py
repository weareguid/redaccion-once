import json
import glob
from pathlib import Path

def combine_notes_to_jsonl():
    """Combine cleaned notes and metadata into a single JSONL file for training."""
    output_file = Path("model_training/data/training_data.jsonl")
    cleaned_dir = Path("cleaned")
    
    # Get all metadata files
    metadata_files = sorted(cleaned_dir.glob("*_metadata.json"))
    
    with output_file.open("w", encoding="utf-8") as f:
        for metadata_file in metadata_files:
            # Get corresponding text file
            text_file = metadata_file.parent / metadata_file.name.replace("_metadata.json", ".txt")
            
            if not text_file.exists():
                print(f"Warning: Missing text file for {metadata_file}")
                continue
                
            try:
                # Read metadata
                with metadata_file.open("r", encoding="utf-8") as mf:
                    metadata = json.load(mf)
                
                # Read text content
                with text_file.open("r", encoding="utf-8") as tf:
                    text = tf.read().strip()
                
                if not text:  # Skip empty notes
                    print(f"Warning: Empty text in {text_file}")
                    continue
                
                # Combine into training format
                training_item = {
                    "text": text,
                    "metadata": metadata
                }
                
                # Write to JSONL file
                f.write(json.dumps(training_item, ensure_ascii=False) + "\n")
                
            except Exception as e:
                print(f"Error processing {metadata_file}: {str(e)}")
    
    print(f"\nTraining data saved to {output_file}")
    # Print some statistics
    with output_file.open("r", encoding="utf-8") as f:
        num_examples = sum(1 for _ in f)
    print(f"Total number of training examples: {num_examples}")

if __name__ == "__main__":
    combine_notes_to_jsonl() 
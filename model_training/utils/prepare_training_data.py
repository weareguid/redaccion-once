import json
import os
from typing import List, Dict
from pathlib import Path

def prepare_training_data(cleaned_dir: str, output_file: str) -> None:
    """
    Prepare training data from cleaned notes in OpenAI's fine-tuning format.
    
    Args:
        cleaned_dir: Directory containing cleaned notes and metadata
        output_file: Path to save the prepared training data
    """
    training_data = []
    metadata_files = [f for f in os.listdir(cleaned_dir) if f.endswith('_metadata.json')]
    
    for metadata_file in sorted(metadata_files):
        base_name = metadata_file.replace('_metadata.json', '')
        content_file = f"{base_name}.txt"
        
        metadata_path = os.path.join(cleaned_dir, metadata_file)
        content_path = os.path.join(cleaned_dir, content_file)
        
        try:
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load content
            if os.path.exists(content_path):
                with open(content_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if "Texto:" in content:
                        content = content.split("Texto:", 1)[1].strip()
                
                # Create training example
                training_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a news article classifier. Classify the following article into the appropriate category and level."
                        },
                        {
                            "role": "user",
                            "content": content
                        },
                        {
                            "role": "assistant",
                            "content": json.dumps({
                                "category": metadata.get('category', ''),
                                "level": metadata.get('level', ''),
                                "title": metadata.get('title', ''),
                                "date": metadata.get('date', '')
                            }, ensure_ascii=False)
                        }
                    ]
                }
                training_data.append(training_example)
            
        except Exception as e:
            print(f"Error processing {base_name}: {str(e)}")
    
    # Save training data
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in training_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"Prepared {len(training_data)} training examples")
    print(f"Training data saved to {output_file}")

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = Path("model_training/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare training data
    prepare_training_data(
        cleaned_dir="cleaned",
        output_file=str(output_dir / "training_data.jsonl")
    ) 
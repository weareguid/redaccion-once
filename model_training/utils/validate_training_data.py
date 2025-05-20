import json
from pathlib import Path
from typing import Dict, List

def validate_training_data(input_file: str) -> Dict:
    """
    Validate the training data format and content.
    
    Args:
        input_file: Path to the training data file
        
    Returns:
        Dict containing validation results
    """
    validation_results = {
        "total_examples": 0,
        "valid_examples": 0,
        "invalid_examples": 0,
        "errors": []
    }
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                validation_results["total_examples"] += 1
                
                try:
                    example = json.loads(line.strip())
                    
                    # Validate structure
                    if not isinstance(example, dict):
                        raise ValueError("Example must be a dictionary")
                    
                    if "messages" not in example:
                        raise ValueError("Missing 'messages' key")
                    
                    messages = example["messages"]
                    if not isinstance(messages, list) or len(messages) != 3:
                        raise ValueError("Must have exactly 3 messages")
                    
                    # Validate message roles
                    roles = [msg.get("role") for msg in messages]
                    if roles != ["system", "user", "assistant"]:
                        raise ValueError("Invalid message roles")
                    
                    # Validate content
                    for msg in messages:
                        if "content" not in msg or not msg["content"]:
                            raise ValueError("Empty message content")
                    
                    # Validate assistant response format
                    try:
                        assistant_content = json.loads(messages[2]["content"])
                        required_fields = ["category", "level", "title", "date"]
                        for field in required_fields:
                            if field not in assistant_content:
                                raise ValueError(f"Missing field in assistant response: {field}")
                    except json.JSONDecodeError:
                        raise ValueError("Assistant response must be valid JSON")
                    
                    validation_results["valid_examples"] += 1
                    
                except Exception as e:
                    validation_results["invalid_examples"] += 1
                    validation_results["errors"].append(f"Line {line_num}: {str(e)}")
        
        return validation_results
        
    except Exception as e:
        return {
            "total_examples": 0,
            "valid_examples": 0,
            "invalid_examples": 0,
            "errors": [f"File error: {str(e)}"]
        }

if __name__ == "__main__":
    input_file = Path("model_training/data/training_data.jsonl")
    
    if not input_file.exists():
        print(f"Error: Training data file not found at {input_file}")
        exit(1)
    
    results = validate_training_data(str(input_file))
    
    print("\nValidation Results:")
    print(f"Total examples: {results['total_examples']}")
    print(f"Valid examples: {results['valid_examples']}")
    print(f"Invalid examples: {results['invalid_examples']}")
    
    if results["errors"]:
        print("\nErrors found:")
        for error in results["errors"]:
            print(f"- {error}")
    else:
        print("\nNo errors found. Training data is valid!") 
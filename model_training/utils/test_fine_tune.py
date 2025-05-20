import os
from pathlib import Path
from model_training.config.training_config import TrainingConfig
from model_training.trainer.fine_tune import FineTuner
import torch

def test_fine_tune_setup():
    """Test the fine-tuning setup."""
    print("Testing fine-tuning setup...")
    
    # Test configuration
    print("\n1. Testing configuration...")
    try:
        config = TrainingConfig.from_env()
        print("✅ Configuration loaded successfully")
        print("\nConfiguration:")
        for key, value in config.to_dict().items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return
    
    # Test CUDA availability
    print("\n2. Testing CUDA availability...")
    if torch.cuda.is_available():
        print(f"✅ CUDA is available. Device: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️ CUDA is not available. Training will be slower on CPU")
    
    # Test training file
    print("\n3. Testing training file...")
    training_file = Path(config.training_file)
    if not training_file.exists():
        print(f"❌ Training file not found: {training_file}")
        return
    print(f"✅ Training file found: {training_file}")
    print(f"   Size: {training_file.stat().st_size / 1024:.2f} KB")
    
    # Test fine-tuner initialization
    print("\n4. Testing fine-tuner initialization...")
    try:
        fine_tuner = FineTuner(config)
        print("✅ Fine-tuner initialized successfully")
    except Exception as e:
        print(f"❌ Fine-tuner initialization error: {str(e)}")
        return
    
    print("\nFine-tuning setup is ready!")
    print("\nTo start fine-tuning, run:")
    print("python -m model_training.trainer.fine_tune")

if __name__ == "__main__":
    test_fine_tune_setup() 
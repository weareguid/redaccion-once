import os
from pathlib import Path
from model_training.config.training_config import TrainingConfig

def test_config():
    """Test the training configuration."""
    print("Testing default configuration...")
    config = TrainingConfig()
    print("\nDefault settings:")
    for key, value in config.to_dict().items():
        print(f"{key}: {value}")
    
    print("\nTesting environment variables...")
    # Set some environment variables
    os.environ["MODEL_NAME"] = "gpt-3.5-turbo-0125"
    os.environ["FT_LR_MULTIPLIER"] = "0.05"
    os.environ["BATCH_SIZE"] = "8"
    os.environ["N_EPOCHS"] = "5"
    os.environ["TEMPERATURE"] = "0.3"
    os.environ["TOP_P"] = "0.95"
    
    config_env = TrainingConfig.from_env()
    print("\nEnvironment-based settings:")
    for key, value in config_env.to_dict().items():
        print(f"{key}: {value}")
    
    print("\nTesting validation...")
    try:
        # Test invalid temperature
        config.temperature = 2.5
        print("❌ Temperature validation failed")
    except ValueError as e:
        print("✅ Temperature validation passed")
    
    try:
        # Test invalid validation split
        config.validation_split = 1.5
        print("❌ Validation split validation failed")
    except ValueError as e:
        print("✅ Validation split validation passed")
    
    try:
        # Test invalid model
        config.model = "invalid-model"
        print("❌ Model validation failed")
    except ValueError as e:
        print("✅ Model validation passed")
    
    try:
        # Test invalid top_p
        config.top_p = 1.5
        print("❌ Top-p validation failed")
    except ValueError as e:
        print("✅ Top-p validation passed")
    
    print("\nTesting directory creation...")
    test_dir = "test_models"
    config.output_dir = test_dir
    print(f"Created directory: {test_dir}")
    
    # Clean up
    if os.path.exists(test_dir):
        os.rmdir(test_dir)
        print(f"Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    test_config() 
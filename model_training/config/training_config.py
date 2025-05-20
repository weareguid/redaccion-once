"""
Configuration for DeepSeek model fine-tuning.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import json
from pathlib import Path
from dataclasses import dataclass
import os

@dataclass
class TrainingConfig:
    """Configuration for model fine-tuning."""
    
    # Model Configuration
    model: str = "deepseek-ai/deepseek-llm-7b-base"  # Base model for text generation
    n_epochs: int = 3  # Reduced epochs for faster training
    batch_size: int = 1  # Keep small for memory efficiency
    max_tokens: int = 1024  # Adjusted for typical article length
    
    # Training Data
    training_file: str = "model_training/data/training_data.jsonl"
    validation_split: float = 0.15  # Balanced validation split
    
    # Hyperparameters
    learning_rate: float = 2e-5  # Standard learning rate for fine-tuning
    weight_decay: float = 0.01  # Standard weight decay
    warmup_steps: int = 100  # Standard warmup steps
    gradient_accumulation_steps: int = 8  # Balanced for CPU training
    
    # Memory Optimizations
    use_8bit: bool = False  # Disable 8-bit quantization for CPU training
    use_gradient_checkpointing: bool = True  # Enable gradient checkpointing
    
    # Output Configuration
    output_dir: str = "models"  # Directory to save fine-tuned models
    model_suffix: str = "news_generator"  # Updated suffix
    
    # Monitoring
    wandb_project: Optional[str] = None  # Weights & Biases project name
    log_every_n_steps: int = 10
    
    def __post_init__(self):
        """Validate and process configuration after initialization."""
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate training file exists
        if not os.path.exists(self.training_file):
            raise FileNotFoundError(f"Training file not found: {self.training_file}")
        
        # Validate hyperparameters
        if not 0 < self.learning_rate < 1:
            raise ValueError("Learning rate must be between 0 and 1")
        if not 0 <= self.validation_split < 1:
            raise ValueError("Validation split must be between 0 and 1")
        if not 0 <= self.weight_decay < 1:
            raise ValueError("Weight decay must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for training."""
        return {
            "model": self.model,
            "n_epochs": self.n_epochs,
            "batch_size": self.batch_size,
            "max_tokens": self.max_tokens,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "warmup_steps": self.warmup_steps,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "use_8bit": self.use_8bit,
            "use_gradient_checkpointing": self.use_gradient_checkpointing
        }
    
    def get_model_name(self) -> str:
        """Generate model name with suffix."""
        return f"{self.model}-{self.model_suffix}"
    
    @classmethod
    def from_env(cls) -> 'TrainingConfig':
        """Create configuration from environment variables."""
        return cls(
            model=os.getenv("MODEL_NAME", "deepseek-ai/deepseek-llm-7b-base"),
            n_epochs=int(os.getenv("N_EPOCHS", "3")),
            batch_size=int(os.getenv("BATCH_SIZE", "1")),
            max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
            learning_rate=float(os.getenv("LEARNING_RATE", "2e-5")),
            weight_decay=float(os.getenv("WEIGHT_DECAY", "0.01")),
            warmup_steps=int(os.getenv("WARMUP_STEPS", "100")),
            gradient_accumulation_steps=int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "8")),
            use_8bit=os.getenv("USE_8BIT", "False").lower() == "true",
            use_gradient_checkpointing=os.getenv("USE_GRADIENT_CHECKPOINTING", "True").lower() == "true",
            output_dir=os.getenv("MODELS_DIR", "models"),
            model_suffix=os.getenv("MODEL_SUFFIX", "news_generator"),
            wandb_project=os.getenv("WANDB_PROJECT"),
            log_every_n_steps=int(os.getenv("LOG_EVERY_N_STEPS", "10"))
        )

if __name__ == '__main__':
    # Example usage
    config = TrainingConfig()
    print("Default configuration:")
    print(config.to_dict())
    
    # Example with environment variables
    os.environ["MODEL_NAME"] = "deepseek-ai/deepseek-llm-7b-base"
    os.environ["N_EPOCHS"] = "3"
    os.environ["BATCH_SIZE"] = "1"
    os.environ["MAX_TOKENS"] = "1024"
    os.environ["LEARNING_RATE"] = "2e-5"
    os.environ["WEIGHT_DECAY"] = "0.01"
    os.environ["WARMUP_STEPS"] = "100"
    os.environ["GRADIENT_ACCUMULATION_STEPS"] = "8"
    os.environ["USE_8BIT"] = "False"
    os.environ["USE_GRADIENT_CHECKPOINTING"] = "True"
    os.environ["MODELS_DIR"] = "models"
    os.environ["MODEL_SUFFIX"] = "news_generator"
    os.environ["WANDB_PROJECT"] = "https://wandb.ai/rodrigo-garciaresendiz-noba"
    os.environ["LOG_EVERY_N_STEPS"] = "10"
    config_env = TrainingConfig.from_env()
    print("\nConfiguration from environment:")
    print(config_env.to_dict()) 
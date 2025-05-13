import os
import time
from pathlib import Path
from typing import Dict, Optional
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from model_training.config.training_config import TrainingConfig
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable tokenizers parallelism
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class FineTuner:
    """Handles the fine-tuning process for text generation."""
    
    def __init__(self, config: TrainingConfig):
        """Initialize the fine-tuner with configuration."""
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Configure quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config.model)
        self.model = AutoModelForCausalLM.from_pretrained(
            config.model,
            quantization_config=quantization_config,
            device_map="auto",
            use_cache=False
        )
        
        # Prepare model for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=16,  # LoRA attention dimension
            lora_alpha=32,  # LoRA alpha parameter
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        # Get PEFT model
        self.model = get_peft_model(self.model, lora_config)
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.eos_token_id
    
    def prepare_dataset(self):
        """Prepare the dataset for training."""
        logger.info("Loading and preparing dataset...")
        
        # Load dataset
        dataset = load_dataset(
            "json",
            data_files=self.config.training_file,
            split="train"
        )
        print("[DEBUG] Loaded dataset columns:", dataset.column_names)
        print("[DEBUG] First example:", dataset[0])
        
        # Split into train and validation
        split_dataset = dataset.train_test_split(
            test_size=self.config.validation_split,
            seed=42
        )
        print("[DEBUG] Train split columns:", split_dataset["train"].column_names)
        print("[DEBUG] First train example:", split_dataset["train"][0])
        print("[DEBUG] Validation split columns:", split_dataset["test"].column_names)
        print("[DEBUG] First validation example:", split_dataset["test"][0])
        
        # Format the text for training
        def format_text(example):
            # Use the 'text' field directly
            return {"text": example["text"]}
        
        # Apply formatting
        formatted_train = split_dataset["train"].map(format_text)
        formatted_val = split_dataset["test"].map(format_text)
        
        # Tokenize function
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=self.config.max_tokens
            )
        
        # Tokenize datasets
        tokenized_train = formatted_train.map(
            tokenize_function,
            batched=True,
            remove_columns=formatted_train.column_names
        )
        tokenized_val = formatted_val.map(
            tokenize_function,
            batched=True,
            remove_columns=formatted_val.column_names
        )
        
        return tokenized_train, tokenized_val
    
    def train(self):
        """Run the fine-tuning process."""
        try:
            # Prepare dataset
            train_dataset, val_dataset = self.prepare_dataset()
            
            # Training arguments
            training_args = TrainingArguments(
                run_name="news_generator_run",
                output_dir=self.config.output_dir,
                num_train_epochs=self.config.n_epochs,
                per_device_train_batch_size=self.config.batch_size,
                per_device_eval_batch_size=self.config.batch_size,
                learning_rate=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
                warmup_steps=self.config.warmup_steps,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                evaluation_strategy="steps",
                eval_steps=100,
                save_strategy="steps",
                save_steps=100,
                logging_steps=self.config.log_every_n_steps,
                load_best_model_at_end=True,
                report_to="wandb" if self.config.wandb_project else None,
                fp16=True,
                optim="adamw_torch_fused",
                dataloader_pin_memory=True
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                data_collator=DataCollatorForLanguageModeling(
                    tokenizer=self.tokenizer,
                    mlm=False
                )
            )
            
            # Start training
            logger.info("Starting training...")
            trainer.train()
            
            # Save final model
            output_path = Path(self.config.output_dir) / self.config.get_model_name()
            trainer.save_model(str(output_path))
            self.tokenizer.save_pretrained(str(output_path))
            
            logger.info(f"Training completed. Model saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            return None

def main():
    """Main function to run the fine-tuning process."""
    try:
        # Load configuration
        config = TrainingConfig.from_env()
        
        # Initialize fine-tuner
        fine_tuner = FineTuner(config)
        
        # Run training
        model_path = fine_tuner.train()
        
        if model_path:
            print(f"\nFine-tuning completed successfully!")
            print(f"Model saved to: {model_path}")
        else:
            print("\nFine-tuning failed. Check the logs for details.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 
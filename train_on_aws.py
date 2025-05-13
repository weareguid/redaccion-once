import boto3
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
import json

def download_from_s3(bucket_name, s3_key, local_path):
    """Download a file from S3 bucket."""
    try:
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, s3_key, local_path)
        print(f"Successfully downloaded {s3_key} to {local_path}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def upload_model_to_s3(bucket_name, local_model_path, s3_key):
    """Upload trained model to S3 bucket."""
    try:
        s3_client = boto3.client('s3')
        for root, dirs, files in os.walk(local_model_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_file_path = os.path.join(s3_key, os.path.relpath(local_file_path, local_model_path))
                s3_client.upload_file(local_file_path, bucket_name, s3_file_path)
        print(f"Successfully uploaded model to {bucket_name}/{s3_key}")
        return True
    except Exception as e:
        print(f"Error uploading model: {e}")
        return False

def train_model(bucket_name, model_name="deepseek-ai/deepseek-coder-6.7b-base"):
    """Train the model using the provided training data."""
    # Load training data
    with open('training_data.json', 'r') as f:
        data = json.load(f)
    
    # Convert to dataset format
    dataset = Dataset.from_dict({
        'text': [item['text'] for item in data]
    })
    
    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Configure training arguments for CPU
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Reduced batch size for CPU
        learning_rate=2e-5,
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=100,
        # CPU-specific optimizations
        no_cuda=True,
        dataloader_num_workers=4,
        gradient_accumulation_steps=4,  # Accumulate gradients to simulate larger batch size
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )
    
    # Train the model
    trainer.train()
    
    # Save the model
    model.save_pretrained("./model")
    tokenizer.save_pretrained("./model")
    
    # Upload model to S3
    s3_client = boto3.client('s3')
    for root, dirs, files in os.walk("./model"):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"models/{os.path.relpath(local_path, './model')}"
            s3_client.upload_file(local_path, bucket_name, s3_path)

def main():
    bucket_name = 'nobanofi-training-bucket'  # Replace with your bucket name
    train_model(bucket_name)

if __name__ == "__main__":
    main() 
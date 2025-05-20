#!/bin/bash

# Training and Upload Script
# This script manages the training process and uploads the model to S3

# Load instance information
if [ -f .aws_instance ]; then
    source .aws_instance
else
    echo "Instance information not found. Please run setup_aws.sh first."
    exit 1
fi

# Configuration
S3_BUCKET="nobanofi-model-training"  # Updated S3 bucket name
MODEL_NAME="deepseek-lora"
LOG_FILE="training.log"

# Activate virtual environment
source venv/bin/activate

# Start monitoring in background
./monitor_training.sh > monitoring.log 2>&1 &
MONITOR_PID=$!

# Start training with logging
echo "Starting training at $(date)" | tee -a $LOG_FILE
python model_training/trainer/fine_tune.py 2>&1 | tee -a $LOG_FILE
TRAINING_EXIT_CODE=${PIPESTATUS[0]}

# Stop monitoring
kill $MONITOR_PID

# Check if training was successful
if [ $TRAINING_EXIT_CODE -eq 0 ]; then
    echo "Training completed successfully at $(date)" | tee -a $LOG_FILE
    
    # Upload model and logs to S3
    echo "Uploading model and logs to S3..." | tee -a $LOG_FILE
    aws s3 cp model_training/models/$MODEL_NAME \
        s3://$S3_BUCKET/$MODEL_NAME --recursive
    aws s3 cp $LOG_FILE s3://$S3_BUCKET/logs/
    aws s3 cp monitoring.log s3://$S3_BUCKET/logs/
    
    if [ $? -eq 0 ]; then
        echo "Model and logs uploaded successfully to s3://$S3_BUCKET" | tee -a $LOG_FILE
    else
        echo "Failed to upload model or logs to S3" | tee -a $LOG_FILE
        exit 1
    fi
else
    echo "Training failed at $(date)" | tee -a $LOG_FILE
    exit 1
fi

# Optional: Terminate instance
read -p "Do you want to terminate the instance? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Terminating instance..." | tee -a $LOG_FILE
    aws ec2 terminate-instances --instance-ids $INSTANCE_ID
    echo "Instance terminated." | tee -a $LOG_FILE
fi 
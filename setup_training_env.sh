#!/bin/bash

# Training Environment Setup Script
# This script sets up the environment for model training on AWS

# Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Install git if not present
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo apt-get install -y git
fi

# Clone repository
echo "Cloning repository..."
git clone https://github.com/<YOUR-ORG>/asistente-redaccion.git
cd asistente-redaccion

# Create and activate virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -U pip
pip install -U accelerate peft bitsandbytes transformers==4.40.0 \
            trl datasets docx2txt chromadb

# Verify GPU
echo "Verifying GPU..."
nvidia-smi

# Verify PyTorch installation
echo "Verifying PyTorch installation..."
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

echo "Setup complete! You can now run the training script." 
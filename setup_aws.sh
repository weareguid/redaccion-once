#!/bin/bash

# AWS Setup Script for Model Training
# This script helps set up an AWS instance for model training

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install it first."
    exit 1
fi

# Configuration
INSTANCE_TYPE="t2.medium"  # 2 vCPUs, CPU-only instance for testing
AMI_ID="ami-0c7217cdde317cfec"  # Deep Learning AMI (Ubuntu 22.04) with PyTorch 2.2
VOLUME_SIZE=100
KEY_NAME="gpu-key"
SECURITY_GROUP_NAME="training-sg"

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh

# Create key pair if it doesn't exist
if [ ! -f ~/.ssh/$KEY_NAME.pem ]; then
    echo "Creating key pair..."
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ~/.ssh/$KEY_NAME.pem
    chmod 400 ~/.ssh/$KEY_NAME.pem
    echo "Key pair created successfully."
else
    echo "Key pair already exists."
fi

# Create security group if it doesn't exist
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME &> /dev/null; then
    echo "Creating security group..."
    aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for model training"
    
    # Get your IP address
    MY_IP=$(curl -s https://checkip.amazonaws.com)
    
    # Allow SSH access
    aws ec2 authorize-security-group-ingress \
        --group-name $SECURITY_GROUP_NAME \
        --protocol tcp \
        --port 22 \
        --cidr $MY_IP/32
    echo "Security group created successfully."
else
    echo "Security group already exists."
fi

# Launch on-demand instance
echo "Launching on-demand instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-groups $SECURITY_GROUP_NAME \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=$VOLUME_SIZE,VolumeType=gp3}" \
    --query 'Instances[0].InstanceId' \
    --output text)

if [ -z "$INSTANCE_ID" ]; then
    echo "Failed to launch instance. Please check your AWS configuration."
    exit 1
fi

echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get instance public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

if [ -z "$PUBLIC_IP" ]; then
    echo "Failed to get public IP. Please check the instance status."
    exit 1
fi

echo "Instance is ready!"
echo "SSH command: ssh -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"

# Save instance information
echo "INSTANCE_ID=$INSTANCE_ID" > .aws_instance
echo "PUBLIC_IP=$PUBLIC_IP" >> .aws_instance
echo "KEY_NAME=$KEY_NAME" >> .aws_instance

# Create monitoring script
cat > monitor_training.sh << 'EOF'
#!/bin/bash

# Monitoring script for training progress
while true; do
    echo "=== $(date) ==="
    echo "GPU Usage:"
    nvidia-smi
    echo "Memory Usage:"
    free -h
    echo "Disk Usage:"
    df -h
    echo "Training Log:"
    tail -n 20 training.log
    echo "=================="
    sleep 300  # Update every 5 minutes
done
EOF

chmod +x monitor_training.sh

echo "Setup complete! You can now SSH into your instance."
echo "To monitor training progress, run: ./monitor_training.sh" 
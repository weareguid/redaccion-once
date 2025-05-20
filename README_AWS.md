# AWS Training Setup

This repository contains scripts for setting up and running model training on AWS.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured with your credentials
3. Python 3.8 or higher
4. Required Python packages (install using `pip install -r requirements_aws.txt`)

## Setup Steps

1. **Configure AWS Credentials**
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and preferred region.

2. **Create Security Group**
   - Create a security group in AWS EC2 console
   - Allow inbound SSH (port 22) from your IP
   - Note down the security group ID

3. **Create Key Pair**
   - Create a new key pair in AWS EC2 console
   - Download the .pem file
   - Note down the key pair name

4. **Update Configuration**
   - Open `aws_setup.py`
   - Replace `your-key-pair-name` with your key pair name
   - Replace `your-security-group-id` with your security group ID
   - Replace `your-training-bucket-name` with your desired bucket name

5. **Run Setup Script**
   ```bash
   python aws_setup.py
   ```
   This will:
   - Create an S3 bucket
   - Upload training data
   - Launch an EC2 instance with Deep Learning AMI

6. **Connect to EC2 Instance**
   ```bash
   ssh -i /path/to/your-key.pem ec2-user@your-instance-public-dns
   ```

7. **Install Dependencies on EC2**
   ```bash
   pip install -r requirements_aws.txt
   ```

8. **Run Training**
   ```bash
   python train_on_aws.py
   ```

## Monitoring

- Monitor training progress in the EC2 instance logs
- Check S3 bucket for saved model artifacts
- Monitor EC2 instance status in AWS Console

## Cleanup

Remember to:
1. Stop the EC2 instance when training is complete
2. Delete the S3 bucket if no longer needed
3. Terminate the EC2 instance to avoid ongoing charges

## Notes

- The training script uses the DeepSeek model by default
- Training parameters can be adjusted in `train_on_aws.py`
- Make sure your EC2 instance has sufficient storage and memory
- Consider using spot instances for cost savings 
import boto3
import os
import time
from botocore.exceptions import ClientError

def create_s3_bucket(bucket_name, region='us-east-1'):
    """Create an S3 bucket for storing training data and model artifacts."""
    try:
        s3_client = boto3.client('s3', region_name=region)
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print(f"Successfully created bucket {bucket_name}")
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        raise

def upload_to_s3(bucket_name, file_path, s3_key):
    """Upload a file to S3 bucket."""
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"Successfully uploaded {file_path} to {bucket_name}/{s3_key}")
    except ClientError as e:
        print(f"Error uploading file: {e}")
        raise

def launch_ec2_instance(instance_type='c5.2xlarge', region='us-east-1'):
    """Launch an EC2 instance using the latest Deep Learning AMI."""
    try:
        ec2_client = boto3.client('ec2', region_name=region)
        
        # Get the latest Deep Learning AMI ID
        response = ec2_client.describe_images(
            Filters=[
                {
                    'Name': 'name',
                    'Values': ['Deep Learning AMI (Amazon Linux 2) Version *']
                },
                {
                    'Name': 'state',
                    'Values': ['available']
                }
            ],
            Owners=['amazon']
        )
        
        # Sort by creation date and get the latest
        latest_ami = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)[0]
        ami_id = latest_ami['ImageId']
        
        # Launch the instance
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName='gpu-key',  # Using your existing key pair
            SecurityGroupIds=['sg-06103b78f71df2aaf'],  # Using your existing security group
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'NOBANOFI-Training'
                        }
                    ]
                }
            ],
            UserData='''#!/bin/bash
            # Install required packages
            sudo yum update -y
            sudo yum install -y python3-pip git unzip
            
            # Install AWS CLI
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            unzip awscliv2.zip
            sudo ./aws/install
            
            # Create project directory
            mkdir -p /home/ec2-user/nobanofi
            
            # Download training data from S3
            aws s3 cp s3://nobanofi-training-bucket/data/training_data.json /home/ec2-user/nobanofi/
            
            # Clone the repository
            git clone https://github.com/weareguid/nobanofi-redaccion.git /home/ec2-user/nobanofi
            
            # Install requirements
            cd /home/ec2-user/nobanofi
            pip3 install -r requirements_aws.txt
            
            # Start training
            python3 train_on_aws.py
            '''
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        print(f"Successfully launched instance {instance_id}")
        return instance_id
        
    except ClientError as e:
        print(f"Error launching instance: {e}")
        raise

def main():
    # Configuration
    bucket_name = 'nobanofi-training-bucket'
    region = 'us-east-1'
    
    # Create S3 bucket
    create_s3_bucket(bucket_name, region)
    
    # Upload training data
    upload_to_s3(bucket_name, 'training_data.json', 'data/training_data.json')
    
    # Launch EC2 instance
    launch_ec2_instance(instance_type='c5.2xlarge', region=region)

if __name__ == '__main__':
    main() 
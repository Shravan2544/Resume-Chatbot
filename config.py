import os

import boto3
import torch
from dotenv import load_dotenv

load_dotenv(override=True)
    
# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# AWS Bedrock client(Using .env variables)
bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
model_id=os.getenv("BEDROCK_MODEL_ID")
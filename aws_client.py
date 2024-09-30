import boto3
import os
from dotenv import load_dotenv

# Load the environment variables once
load_dotenv()

# Fetch AWS credentials and region from environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET = os.getenv("AWS_SECRET")
REGION = os.getenv("REGION")

def get_sqs_client():
    """
    Initializes and returns the SQS client
    """
    return boto3.client(
        'sqs',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET
    )

def get_s3_client():
    """
    Initializes and returns the S3 client
    """
    return boto3.client(
        's3',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET
    )

from fastapi import FastAPI
import boto3
import json
import os
from dotenv import load_dotenv
app = FastAPI()


# Load the environment variables from .env file
load_dotenv()
# Initialize SQS client
sqs = boto3.client( 
     os.getenv("SERVICE_NAME"),
     region_name=os.getenv("REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET")
    )  # Replace 'your-region' with the AWS region you're using

# SQS Queue URL
QUEUE_URL = os.getenv("QUEUE_URL")


@app.get("/")
async def root():
    return {"message": "aman"}



@app.get("/receive-message")
def receive_message():
    try:
        # Receive message from SQS queue
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=2,
            WaitTimeSeconds=10  # Wait up to 10 seconds to receive a message
        )
        
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            body = json.loads(message['Body'])

            # Print the message body
            print("Received message:", body)

            # Optionally, delete the message from the queue after processing
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=receipt_handle
            )
            
            return {"status": "success", "message": body}
        else:
            return {"status": "no messages"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

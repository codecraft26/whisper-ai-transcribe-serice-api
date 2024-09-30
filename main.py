from fastapi import FastAPI, File, UploadFile, HTTPException
import boto3
import json
import os
from dotenv import load_dotenv
app = FastAPI()

from botocore.exceptions import NoCredentialsError
# Load the environment variables from .env file
load_dotenv()
# Initialize SQS client
sqs = boto3.client( 
     os.getenv("SERVICE_NAME"),
     region_name=os.getenv("REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET")
    )  # Replace 'your-region' with the AWS region you're using
# Initialize S3 client
s3 = boto3.client(
    's3',  # S3 service
    region_name=os.getenv("REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET")
)

# SQS Queue URL
QUEUE_URL = os.getenv("QUEUE_URL")
# S3 bucket name
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {'.mp3', '.mp4', '.avi', '.mov','.ts'}
ALLOWED_MIME_TYPES = {'audio/mpeg', 'video/mp4', 'video/x-msvideo', 'video/quicktime'}

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


@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Check the file extension and MIME type
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_mime_type = file.content_type

        if file_extension not in ALLOWED_EXTENSIONS or file_mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"File format not supported. Only MP3 and video files ({', '.join(ALLOWED_EXTENSIONS)}) are allowed."
            )

        # Read the file content
        file_content = await file.read()

        # Upload the file to S3 with public read access
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file.filename,
            Body=file_content,
            ContentType=file.content_type,
            ACL='public-read'  # <-- Add this line to set public access
        )

        # Return the file URL
        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file.filename}"
        return {"status": "success", "file_url": file_url}

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
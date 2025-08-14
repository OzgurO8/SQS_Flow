import boto3
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
QUEUE_UR_TODO = os.getenv('QUEUE_UR_TODO')
QUEUE_UR_COMPLETED = os.getenv('QUEUE_UR_COMPLETED')

# Create SQS client with credentials from environment variables
sqs = boto3.client(
    'sqs',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def delete_message_from_queue(sqs_client, queue_url, receipt_handle):
    """
    Deletes a message from the SQS queue using the provided receipt handle.
    """
    sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )

def move_message_to_another_queue(sqs_client, source_queue_url, dest_queue_url, message):
    """
    Moves a message from the source queue to the destination queue (e.g., a completed queue).
    This is done by sending the message body to the destination queue and then deleting it from the source queue.
    """
    # Send the message to the destination queue
    sqs_client.send_message(
        QueueUrl=dest_queue_url,
        MessageBody=message['Body'],
        MessageAttributes=message.get('MessageAttributes', {})
    )
    # Delete the message from the source queue
    delete_message_from_queue(sqs_client, source_queue_url, message['ReceiptHandle'])

def parse_first_item_from_json(json_string):
    """
    Dummy function that loads a JSON string and returns the first item.
    - If the JSON is a list, returns the first element.
    - If the JSON is a dict, returns the value of the first key in iteration order.
    - Otherwise, returns the parsed JSON as-is.
    """
    try:
        parsed = json.loads(json_string)
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        if isinstance(parsed, dict) and parsed:
            first_key = next(iter(parsed))
            return parsed[first_key]
        return parsed
    except json.JSONDecodeError:
        return None

def receive_messages():
    response = sqs.receive_message(
        QueueUrl=QUEUE_UR_TODO,
        MaxNumberOfMessages=5,      # Adjust as needed (max 10)
        WaitTimeSeconds=2           # Long polling
    )
    messages = response.get('Messages', [])
    for message in messages:
        receipt_handle = message['ReceiptHandle']
        print(f"Processing message: {receipt_handle}")
        first_item = parse_first_item_from_json(message['Body'])
        print("First item:", first_item)
        # Move the processed message to the completed queue
        print(f"Moving message {receipt_handle} to completed queue...")
        move_message_to_another_queue(sqs, QUEUE_UR_TODO, QUEUE_UR_COMPLETED, message)
        print(f"Message {receipt_handle} successfully processed, deleted from TODO queue and moved to COMPLETED queue")

if __name__ == "__main__":
    receive_messages()

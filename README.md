# SQS Message Processor

A Python script that processes messages from an AWS SQS queue, extracts the first item from JSON message bodies, and moves processed messages to a completed queue.

## Features

- Receives messages from a TODO SQS queue
- Parses JSON message bodies and extracts the first item
- Moves processed messages to a COMPLETED queue
- Provides detailed logging of message processing steps
- Uses environment variables for AWS configuration

## Prerequisites

- Python 3.6+
- AWS account with SQS access
- Required Python packages (see Installation)

## Installation

1. Install required dependencies:
```bash
pip install boto3 python-dotenv
```

2. Create a `.env` file in the project root with your AWS credentials and queue URLs:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=your_aws_region
QUEUE_UR_TODO=https://sqs.region.amazonaws.com/account-id/todo-queue-name
QUEUE_UR_COMPLETED=https://sqs.region.amazonaws.com/account-id/completed-queue-name
```

## Usage

Run the script to start processing messages:
```bash
python sqs_receive.py
```

The script will:
1. Poll the TODO queue for messages (up to 5 messages at a time)
2. For each message:
   - Extract the first item from the JSON message body
   - Print processing status and extracted data
   - Move the message from TODO queue to COMPLETED queue
   - Print confirmation of successful processing

## Functions

### `parse_first_item_from_json(json_string)`
Parses a JSON string and returns the first item:
- If JSON is a list: returns the first element
- If JSON is a dict: returns the value of the first key
- Otherwise: returns the parsed JSON as-is
- Returns `None` if JSON parsing fails

### `move_message_to_another_queue(sqs_client, source_queue_url, dest_queue_url, message)`
Moves a message from source queue to destination queue by:
1. Sending the message body to the destination queue
2. Deleting the message from the source queue

### `delete_message_from_queue(sqs_client, queue_url, receipt_handle)`
Deletes a specific message from an SQS queue using its receipt handle.

### `receive_messages()`
Main processing function that:
- Polls the TODO queue for messages
- Processes each message through the JSON parser
- Moves processed messages to the COMPLETED queue

## Configuration

The script uses the following environment variables:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: AWS region (e.g., `us-east-1`)
- `QUEUE_UR_TODO`: URL of the TODO SQS queue
- `QUEUE_UR_COMPLETED`: URL of the COMPLETED SQS queue

## Example Output

```
Processing message: AQEBwJnKyrHigUMZj6rYigEgVXQiG4QaeFhiS+/VbHjowAaJkRwaq...
First item: {"id": 123, "task": "Process order"}
Moving message AQEBwJnKyrHigUMZj6rYigEgVXQiG4QaeFhiS+/VbHjowAaJkRwaq... to completed queue...
Message AQEBwJnKyrHigUMZj6rYigEgVXQiG4QaeFhiS+/VbHjowAaJkRwaq... successfully processed, deleted from TODO queue and moved to COMPLETED queue
```

## Error Handling

- JSON parsing errors are handled gracefully (returns `None`)
- AWS API errors will be raised and should be handled by the calling code
- Environment variable validation should be added for production use

## Notes

- The script uses long polling with a 2-second wait time
- Maximum 5 messages are processed per polling cycle
- Messages are automatically deleted from the source queue after successful processing

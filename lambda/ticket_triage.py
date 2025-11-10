import json
import boto3
import os
from datetime import datetime
import uuid

bedrock_agent = boto3.client('bedrock-agent-runtime')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
s3 = boto3.client('s3')

KB_ID = os.environ.get('KNOWLEDGE_BASE_ID', 'test-kb-id')
TABLE_NAME = os.environ.get('TABLE_NAME', 'test-table')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL', 'noreply@example.com')

def handler(event, context):
    """
    Process incoming tickets from S3 and perform triage using Bedrock KB.
    """
    try:
        # Get ticket from S3
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # Read ticket content
            response = s3.get_object(Bucket=bucket, Key=key)
            ticket_content = response['Body'].read().decode('utf-8')

            # Parse ticket (assume JSON format)
            try:
                ticket = json.loads(ticket_content)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                ticket = {
                    'description': ticket_content,
                    'title': 'Untitled Ticket'
                }

            # Generate ticket ID if not present
            ticket_id = ticket.get('id', str(uuid.uuid4()))

            # Query knowledge base for triage
            triage_result = perform_triage(ticket)

            # Store result in DynamoDB
            table = dynamodb.Table(TABLE_NAME)
            item = {
                'ticketId': ticket_id,
                'timestamp': int(datetime.utcnow().timestamp()),
                'status': 'triaged',
                'ticketTitle': ticket.get('title', 'Untitled'),
                'ticketDescription': ticket.get('description', '')[:500],
                'category': triage_result['category'],
                'priority': triage_result['priority'],
                'suggestedActions': triage_result['actions'],
                'kbResponse': triage_result['kb_response'][:1000],
                's3Key': key
            }
            table.put_item(Item=item)

            # Send email notification if email provided
            if ticket.get('email'):
                send_email_notification(ticket, triage_result)

        return {
            'statusCode': 200,
            'body': json.dumps('Triage completed successfully')
        }

    except Exception as e:
        print(f'Error processing ticket: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def perform_triage(ticket):
    """
    Use Bedrock Knowledge Base to triage the ticket.
    """
    # Construct query for knowledge base
    query = f"""
    Analyze this HPC-related support ticket and provide triage information:

    Title: {ticket.get('title', 'N/A')}
    Description: {ticket.get('description', 'N/A')}

    Please provide:
    1. Category (e.g., NCCL, RCCL, CUDA, Networking, Performance, Other)
    2. Priority (High, Medium, Low)
    3. Suggested actions or troubleshooting steps
    """

    try:
        # Query knowledge base
        response = bedrock_agent.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KB_ID,
                    'modelArn': f'arn:aws:bedrock:{os.environ.get("AWS_REGION", "us-east-1")}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                }
            }
        )

        kb_response = response['output']['text']

        # Parse response to extract triage info
        triage = parse_triage_response(kb_response)
        triage['kb_response'] = kb_response

        return triage

    except Exception as e:
        print(f'Error querying knowledge base: {str(e)}')
        # Return default triage if KB query fails
        return {
            'category': 'Other',
            'priority': 'Medium',
            'actions': ['Manual review required'],
            'kb_response': f'Error: {str(e)}'
        }

def parse_triage_response(response):
    """
    Parse the KB response to extract category, priority, and actions.
    """
    # Simple parsing - in production, use more robust NLP
    response_lower = response.lower()

    # Determine category
    categories = ['nccl', 'rccl', 'cuda', 'networking', 'performance']
    category = 'Other'
    for cat in categories:
        if cat in response_lower:
            category = cat.upper()
            break

    # Determine priority
    if 'high priority' in response_lower or 'critical' in response_lower:
        priority = 'High'
    elif 'low priority' in response_lower:
        priority = 'Low'
    else:
        priority = 'Medium'

    # Extract actions (look for numbered lists or bullet points)
    actions = []
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            actions.append(line)

    if not actions:
        actions = ['Review ticket and knowledge base response']

    return {
        'category': category,
        'priority': priority,
        'actions': actions[:5]  # Limit to 5 actions
    }

def send_email_notification(ticket, triage_result):
    """
    Send email notification with triage results.
    """
    try:
        subject = f"Ticket Triage: {ticket.get('title', 'Untitled')}"

        body = f"""
Ticket Triage Results

Title: {ticket.get('title', 'Untitled')}
Category: {triage_result['category']}
Priority: {triage_result['priority']}

Suggested Actions:
{chr(10).join(f'- {action}' for action in triage_result['actions'])}

AI Analysis:
{triage_result['kb_response'][:500]}...

This ticket has been automatically triaged using AI and HPC knowledge base.
        """

        ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [ticket['email']]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print(f"Email sent to {ticket['email']}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

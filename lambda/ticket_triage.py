import json
import boto3
import os
from datetime import datetime
import uuid

bedrock_agent = boto3.client('bedrock-agent-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
s3 = boto3.client('s3')

KB_ID = os.environ.get('KNOWLEDGE_BASE_ID')
TABLE_NAME = os.environ.get('TABLE_NAME')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL')
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

def handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            response = s3.get_object(Bucket=bucket, Key=key)
            ticket_content = response['Body'].read().decode('utf-8')

            try:
                ticket = json.loads(ticket_content)
            except json.JSONDecodeError:
                ticket = {'description': ticket_content, 'title': 'Untitled Ticket'}

            ticket_id = ticket.get('id', str(uuid.uuid4()))
            triage_result = perform_triage(ticket)

            table = dynamodb.Table(TABLE_NAME)
            table.put_item(Item={
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
            })

            if ticket.get('email'):
                send_email_notification(ticket, triage_result)

        return {'statusCode': 200, 'body': json.dumps('Triage completed')}

    except Exception as e:
        print(f'Error: {str(e)}')
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}

def perform_triage(ticket):
    query = f"""Analyze this HPC support ticket:

Title: {ticket.get('title', 'N/A')}
Description: {ticket.get('description', 'N/A')}

Provide triage information including category, priority, and suggested actions."""

    try:
        kb_response = bedrock_agent.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KB_ID,
                    'modelArn': f'arn:aws:bedrock:{os.environ.get("AWS_REGION", "us-east-1")}::foundation-model/{MODEL_ID}'
                }
            }
        )

        kb_text = kb_response['output']['text']

        triage_tool = {
            "toolSpec": {
                "name": "ticket_triage",
                "description": "Extract structured triage data from ticket analysis",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["NCCL", "RCCL", "CUDA", "NETWORKING", "PERFORMANCE", "OTHER"],
                                "description": "The primary category of the ticket"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["HIGH", "MEDIUM", "LOW"],
                                "description": "The priority level"
                            },
                            "actions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of suggested troubleshooting steps"
                            }
                        },
                        "required": ["category", "priority", "actions"]
                    }
                }
            }
        }

        structured_response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=[{
                "role": "user",
                "content": [{
                    "text": f"Based on this analysis:\n\n{kb_text}\n\nExtract the category, priority, and suggested actions. Use the ticket_triage tool to provide structured output."
                }]
            }],
            toolConfig={"tools": [triage_tool]}
        )

        if 'toolUse' in structured_response['output']['message']['content'][0]:
            tool_result = structured_response['output']['message']['content'][0]['toolUse']['input']
            return {
                'category': tool_result['category'],
                'priority': tool_result['priority'],
                'actions': tool_result['actions'][:5],
                'kb_response': kb_text
            }

        return {
            'category': 'OTHER',
            'priority': 'MEDIUM',
            'actions': ['Manual review required'],
            'kb_response': kb_text
        }

    except Exception as e:
        print(f'Error in triage: {str(e)}')
        return {
            'category': 'OTHER',
            'priority': 'MEDIUM',
            'actions': ['Manual review required'],
            'kb_response': f'Error: {str(e)}'
        }

def send_email_notification(ticket, triage_result):
    try:
        subject = f"Ticket Triage: {ticket.get('title', 'Untitled')}"
        body = f"""Ticket Triage Results

Title: {ticket.get('title', 'Untitled')}
Category: {triage_result['category']}
Priority: {triage_result['priority']}

Suggested Actions:
{chr(10).join(f'- {action}' for action in triage_result['actions'])}

AI Analysis:
{triage_result['kb_response'][:500]}...

This ticket has been automatically triaged using AI."""

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

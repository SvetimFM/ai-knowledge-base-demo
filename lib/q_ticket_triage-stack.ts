import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as ses from 'aws-cdk-lib/aws-ses';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

export interface QTicketTriageStackProps extends cdk.StackProps {
  presidioKbArn?: string;  // Optional: ARN of Presidio KB for Lambda permissions
}

export class QTicketTriageStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: QTicketTriageStackProps) {
    super(scope, id, props);

    // S3 Bucket for HPC documentation
    const docsBucket = new s3.Bucket(this, 'HpcDocsBucket', {
      bucketName: `hpc-knowledge-base-docs-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create Bedrock Knowledge Base with AWS Labs construct (handles OpenSearch automatically)
    const knowledgeBase = new bedrock.VectorKnowledgeBase(this, 'HpcKnowledgeBase', {
      name: 'hpc-computing-knowledge-base',
      description: 'Knowledge base for HPC computing topics: NCCL, RCCL, CUDA testing, and communication patterns',
      embeddingsModel: bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
      instruction: 'Use this knowledge base to answer questions about HPC computing, including NCCL, RCCL, CUDA testing, communication patterns, and performance optimization.',
    });

    // Tag the knowledge base for MCP server discovery
    cdk.Tags.of(knowledgeBase).add('name', 'true');

    // Add S3 data source to knowledge base
    new bedrock.S3DataSource(this, 'HpcDataSource', {
      bucket: docsBucket,
      knowledgeBase: knowledgeBase,
      dataSourceName: 'hpc-docs-s3-source',
      chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
        maxTokens: 512,
        overlapPercentage: 20,
      }),
    });

    // CloudFormation Outputs for Knowledge Base
    new cdk.CfnOutput(this, 'DocsBucketName', {
      value: docsBucket.bucketName,
      description: 'S3 bucket for HPC documentation',
      exportName: 'HpcDocsBucketName',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseId', {
      value: knowledgeBase.knowledgeBaseId,
      description: 'Bedrock Knowledge Base ID',
      exportName: 'HpcKnowledgeBaseId',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseArn', {
      value: knowledgeBase.knowledgeBaseArn,
      description: 'Bedrock Knowledge Base ARN',
      exportName: 'HpcKnowledgeBaseArn',
    });

    // ==========================================
    // Ticket Triage System Resources
    // ==========================================

    // S3 Bucket for ticket submissions
    const ticketsBucket = new s3.Bucket(this, 'TicketsBucket', {
      bucketName: `hpc-tickets-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // DynamoDB table for triage results
    const triageTable = new dynamodb.Table(this, 'TriageResultsTable', {
      tableName: 'hpc-ticket-triage-results',
      partitionKey: { name: 'ticketId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
    });

    // Add GSI for status queries
    triageTable.addGlobalSecondaryIndex({
      indexName: 'status-index',
      partitionKey: { name: 'status', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
    });

    // Lambda function for ticket triage
    const triageFunction = new lambda.Function(this, 'TicketTriageFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      functionName: 'hpc-ticket-triage-processor',
      code: lambda.Code.fromInline(`
import json
import boto3
import os
from datetime import datetime
import uuid

bedrock_agent = boto3.client('bedrock-agent-runtime')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
s3 = boto3.client('s3')

KB_ID = os.environ['KNOWLEDGE_BASE_ID']
TABLE_NAME = os.environ['TABLE_NAME']
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
                    'modelArn': f'arn:aws:bedrock:{os.environ["AWS_REGION"]}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
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
    lines = response.split('\\n')
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
`),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        KNOWLEDGE_BASE_ID: knowledgeBase.knowledgeBaseId,
        TABLE_NAME: triageTable.tableName,
        SES_FROM_EMAIL: 'noreply@example.com', // Update with your verified SES email
      },
    });

    // Grant Lambda permissions
    triageTable.grantWriteData(triageFunction);
    ticketsBucket.grantRead(triageFunction);

    // Grant Lambda access to Bedrock Knowledge Bases
    const bedrockResources = [
      knowledgeBase.knowledgeBaseArn,  // HPC Knowledge Base
      `arn:aws:bedrock:${this.region}::foundation-model/*`,
    ];

    // Add Presidio KB if provided (cross-stack reference)
    if (props?.presidioKbArn) {
      bedrockResources.push(props.presidioKbArn);
    }

    triageFunction.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'bedrock:InvokeModel',
          'bedrock:Retrieve',
          'bedrock:RetrieveAndGenerate',
        ],
        resources: bedrockResources,
      })
    );

    // Grant Lambda access to SES
    triageFunction.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['ses:SendEmail', 'ses:SendRawEmail'],
        resources: ['*'],
      })
    );

    // Configure S3 bucket notification to trigger Lambda
    ticketsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(triageFunction),
      { suffix: '.json' }
    );

    ticketsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(triageFunction),
      { suffix: '.txt' }
    );

    // Outputs for ticket triage system
    new cdk.CfnOutput(this, 'TicketsBucketName', {
      value: ticketsBucket.bucketName,
      description: 'S3 bucket for ticket submissions',
      exportName: 'HpcTicketsBucketName',
    });

    new cdk.CfnOutput(this, 'TriageTableName', {
      value: triageTable.tableName,
      description: 'DynamoDB table for triage results',
      exportName: 'HpcTriageTableName',
    });

    new cdk.CfnOutput(this, 'TriageFunctionName', {
      value: triageFunction.functionName,
      description: 'Lambda function for ticket triage',
      exportName: 'HpcTriageFunctionName',
    });
  }
}

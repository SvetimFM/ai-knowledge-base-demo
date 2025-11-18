import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export interface TicketTriageStackProps extends cdk.StackProps {
  hpcKbArn: string;
  presidioKbArn?: string;
}

export class TicketTriageStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: TicketTriageStackProps) {
    super(scope, id, props);

    const ticketsBucket = new s3.Bucket(this, 'TicketsBucket', {
      bucketName: `ticket-triage-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    const triageTable = new dynamodb.Table(this, 'TriageResultsTable', {
      tableName: 'ticket-triage-results',
      partitionKey: { name: 'ticketId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
    });

    triageTable.addGlobalSecondaryIndex({
      indexName: 'status-index',
      partitionKey: { name: 'status', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
    });

    const triageFunction = new lambda.Function(this, 'TicketTriageFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'ticket_triage.handler',
      functionName: 'ticket-triage-processor',
      code: lambda.Code.fromAsset('lambda'),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        KNOWLEDGE_BASE_ID: cdk.Fn.select(1, cdk.Fn.split('/', props.hpcKbArn)),
        TABLE_NAME: triageTable.tableName,
        SES_FROM_EMAIL: process.env.SES_FROM_EMAIL || 'noreply@example.com',
      },
    });

    triageTable.grantWriteData(triageFunction);
    ticketsBucket.grantRead(triageFunction);

    const bedrockResources = [
      props.hpcKbArn,
      `arn:aws:bedrock:${this.region}::foundation-model/*`,
    ];
    if (props.presidioKbArn) {
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

    triageFunction.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['ses:SendEmail', 'ses:SendRawEmail'],
        resources: ['*'],
      })
    );

    ['.json', '.txt'].forEach(suffix =>
      ticketsBucket.addEventNotification(
        s3.EventType.OBJECT_CREATED,
        new s3n.LambdaDestination(triageFunction),
        { suffix }
      )
    );
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

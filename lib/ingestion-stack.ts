import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';

export interface IngestionStackProps extends cdk.StackProps {
  embeddingsFunctionArn: string;
}

export class IngestionStack extends cdk.Stack {
  public readonly documentsBucket: s3.Bucket;
  public readonly ingestionQueue: sqs.Queue;
  public readonly stateTable: dynamodb.Table;
  public readonly ingestorFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: IngestionStackProps) {
    super(scope, id, props);

    // S3 Bucket for document uploads
    this.documentsBucket = new s3.Bucket(this, 'DocumentsBucket', {
      bucketName: `kb-documents-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true, // Track document versions
      removalPolicy: cdk.RemovalPolicy.RETAIN, // Don't delete documents on stack deletion
      lifecycleRules: [
        {
          id: 'archive-old-versions',
          noncurrentVersionExpiration: cdk.Duration.days(90),
          enabled: true,
        },
      ],
    });

    // Dead Letter Queue for failed document processing
    const deadLetterQueue = new sqs.Queue(this, 'IngestionDLQ', {
      queueName: 'document-ingestion-dlq.fifo',
      fifo: true,
      retentionPeriod: cdk.Duration.days(14), // Keep failed messages for 2 weeks
      contentBasedDeduplication: true,
    });

    // SQS Queue for S3 event notifications
    this.ingestionQueue = new sqs.Queue(this, 'IngestionQueue', {
      queueName: 'document-ingestion.fifo',
      fifo: true,
      visibilityTimeout: cdk.Duration.minutes(10), // Must be >= Lambda timeout
      receiveMessageWaitTime: cdk.Duration.seconds(20), // Long polling
      deadLetterQueue: {
        queue: deadLetterQueue,
        maxReceiveCount: 3, // Retry 3 times before DLQ
      },
      contentBasedDeduplication: true,
    });

    // S3 → SQS notification for new documents
    this.documentsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(this.ingestionQueue),
      {
        suffix: '.pdf', // Only trigger on PDFs for now
      }
    );

    this.documentsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(this.ingestionQueue),
      {
        suffix: '.md', // Also trigger on markdown
      }
    );

    this.documentsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(this.ingestionQueue),
      {
        suffix: '.txt', // And text files
      }
    );

    // DynamoDB Table for tracking document processing state
    this.stateTable = new dynamodb.Table(this, 'DocumentStateTable', {
      tableName: 'document-ingestion-state',
      partitionKey: {
        name: 's3_uri',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'version_id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST, // On-demand pricing
      removalPolicy: cdk.RemovalPolicy.RETAIN, // Keep state history
      pointInTimeRecovery: true, // Enable backups
    });

    // GSI for querying by knowledge base and status
    this.stateTable.addGlobalSecondaryIndex({
      indexName: 'knowledge_base-status-index',
      partitionKey: {
        name: 'knowledge_base',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'status',
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Document Ingestor Lambda
    this.ingestorFunction = new lambda.Function(this, 'DocumentIngestor', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('lambda/document-ingestor'),
      timeout: cdk.Duration.minutes(10), // Long timeout for large documents
      memorySize: 2048, // More memory for better performance
      reservedConcurrentExecutions: 5, // Limit concurrent executions for cost control
      environment: {
        EMBEDDINGS_FUNCTION_ARN: props.embeddingsFunctionArn,
        DYNAMODB_TABLE_NAME: this.stateTable.tableName,
      },
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    // SQS trigger for ingestor Lambda
    this.ingestorFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(this.ingestionQueue, {
        batchSize: 1, // Process one document at a time
        reportBatchItemFailures: true, // For partial batch failures
      })
    );

    // Grant permissions: S3 read
    this.documentsBucket.grantRead(this.ingestorFunction);

    // Grant permissions: DynamoDB read/write
    this.stateTable.grantReadWriteData(this.ingestorFunction);

    // Grant permissions: Invoke embeddings Lambda
    this.ingestorFunction.addToRolePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['lambda:InvokeFunction'],
        resources: [props.embeddingsFunctionArn],
      })
    );

    // CloudWatch alarm for DLQ depth
    const dlqAlarm = deadLetterQueue.metricApproximateNumberOfMessagesVisible().createAlarm(
      this,
      'DLQAlarm',
      {
        threshold: 1,
        evaluationPeriods: 1,
        alarmDescription: 'Alert when documents fail to process and end up in DLQ',
        treatMissingData: cdk.aws_cloudwatch.TreatMissingData.NOT_BREACHING,
      }
    );

    // Outputs
    new cdk.CfnOutput(this, 'DocumentsBucketName', {
      value: this.documentsBucket.bucketName,
      description: 'S3 bucket for document uploads',
      exportName: 'DocumentsBucketName',
    });

    new cdk.CfnOutput(this, 'IngestionQueueUrl', {
      value: this.ingestionQueue.queueUrl,
      description: 'SQS queue for document processing',
    });

    new cdk.CfnOutput(this, 'StateTableName', {
      value: this.stateTable.tableName,
      description: 'DynamoDB table for tracking document state',
    });

    new cdk.CfnOutput(this, 'IngestorFunctionName', {
      value: this.ingestorFunction.functionName,
      description: 'Lambda function for document ingestion',
    });

    new cdk.CfnOutput(this, 'UploadCommand', {
      value: `aws s3 cp your-document.pdf s3://${this.documentsBucket.bucketName}/hpc/`,
      description: 'Example command to upload a document to HPC knowledge base',
    });
  }
}

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

export class PresidioKnowledgeBaseStack extends cdk.Stack {
  public readonly presidioKbArn: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 Bucket for Presidio documentation
    const presidioDocsBucket = new s3.Bucket(this, 'PresidioDocsBucket', {
      bucketName: `presidio-knowledge-base-docs-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create Presidio Bedrock Knowledge Base
    const presidioKnowledgeBase = new bedrock.VectorKnowledgeBase(this, 'PresidioKnowledgeBase', {
      name: 'presidio-solutions-knowledge-base',
      description: 'Knowledge base for Presidio IT solutions: cloud, security, AI, data center modernization, networking, and managed services',
      embeddingsModel: bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
      instruction: 'Use this knowledge base to answer questions about Presidio IT solutions and services, including cloud migration, cybersecurity, AI/ML platforms, data center modernization, networking, collaboration, managed services, and industry-specific implementations.',
    });

    // Tag the Presidio knowledge base for MCP server discovery (same tag as HPC KB)
    cdk.Tags.of(presidioKnowledgeBase).add('name', 'true');

    // Add S3 data source to Presidio knowledge base
    new bedrock.S3DataSource(this, 'PresidioDataSource', {
      bucket: presidioDocsBucket,
      knowledgeBase: presidioKnowledgeBase,
      dataSourceName: 'presidio-docs-s3-source',
      chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
        maxTokens: 512,
        overlapPercentage: 20,
      }),
    });

    // CloudFormation Outputs for Presidio Knowledge Base
    new cdk.CfnOutput(this, 'PresidioDocsBucketName', {
      value: presidioDocsBucket.bucketName,
      description: 'S3 bucket for Presidio documentation',
      exportName: 'PresidioDocsBucketName',
    });

    new cdk.CfnOutput(this, 'PresidioKnowledgeBaseId', {
      value: presidioKnowledgeBase.knowledgeBaseId,
      description: 'Presidio Bedrock Knowledge Base ID',
      exportName: 'PresidioKnowledgeBaseId',
    });

    new cdk.CfnOutput(this, 'PresidioKnowledgeBaseArn', {
      value: presidioKnowledgeBase.knowledgeBaseArn,
      description: 'Presidio Bedrock Knowledge Base ARN',
      exportName: 'PresidioKnowledgeBaseArn',
    });

    // Export for cross-stack reference
    this.presidioKbArn = presidioKnowledgeBase.knowledgeBaseArn;
  }
}

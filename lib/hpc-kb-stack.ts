import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

export class HpcKnowledgeBaseStack extends cdk.Stack {
  public readonly hpcKbArn: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
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

    // Export for cross-stack reference
    this.hpcKbArn = knowledgeBase.knowledgeBaseArn;
  }
}

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

export interface KnowledgeBaseProps {
  name: string;
  description: string;
  instruction: string;
  bucketPrefix: string;
}

export class KnowledgeBaseConstruct extends Construct {
  public readonly knowledgeBase: bedrock.VectorKnowledgeBase;
  public readonly bucket: s3.Bucket;
  public readonly dataSource: bedrock.S3DataSource;

  constructor(scope: Construct, id: string, props: KnowledgeBaseProps) {
    super(scope, id);

    const account = cdk.Stack.of(this).account;

    this.bucket = new s3.Bucket(this, 'Bucket', {
      bucketName: `${props.bucketPrefix}-${account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    this.knowledgeBase = new bedrock.VectorKnowledgeBase(this, 'KB', {
      name: props.name,
      description: props.description,
      embeddingsModel: bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
      instruction: props.instruction,
    });

    cdk.Tags.of(this.knowledgeBase).add('name', 'true');

    this.dataSource = new bedrock.S3DataSource(this, 'DataSource', {
      bucket: this.bucket,
      knowledgeBase: this.knowledgeBase,
      dataSourceName: `${props.bucketPrefix}-source`,
      chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
        maxTokens: 512,
        overlapPercentage: 20,
      }),
    });
  }
}

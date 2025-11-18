import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { KnowledgeBaseConstruct } from './knowledge-base-construct';

export class HpcKnowledgeBaseStack extends cdk.Stack {
  public readonly kbArn: string;
  public readonly dataSourceId: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const kb = new KnowledgeBaseConstruct(this, 'HpcKB', {
      name: 'hpc-computing-knowledge-base',
      description: 'Knowledge base for HPC computing topics: NCCL, RCCL, CUDA testing, and communication patterns',
      instruction: 'Use this knowledge base to answer questions about HPC computing, including NCCL, RCCL, CUDA testing, communication patterns, and performance optimization.',
      bucketPrefix: 'hpc-kb-docs',
    });

    new cdk.CfnOutput(this, 'BucketName', {
      value: kb.bucket.bucketName,
      exportName: 'HpcDocsBucketName',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseId', {
      value: kb.knowledgeBase.knowledgeBaseId,
      exportName: 'HpcKnowledgeBaseId',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseArn', {
      value: kb.knowledgeBase.knowledgeBaseArn,
      exportName: 'HpcKnowledgeBaseArn',
    });

    new cdk.CfnOutput(this, 'DataSourceId', {
      value: kb.dataSource.dataSourceId,
      exportName: 'HpcDataSourceId',
    });

    this.kbArn = kb.knowledgeBase.knowledgeBaseArn;
    this.dataSourceId = kb.dataSource.dataSourceId;
  }
}

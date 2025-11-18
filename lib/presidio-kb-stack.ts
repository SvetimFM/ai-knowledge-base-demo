import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { KnowledgeBaseConstruct } from './knowledge-base-construct';

export class PresidioKnowledgeBaseStack extends cdk.Stack {
  public readonly kbArn: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const kb = new KnowledgeBaseConstruct(this, 'PresidioKB', {
      name: 'presidio-solutions-knowledge-base',
      description: 'Knowledge base for Presidio IT solutions: cloud, security, AI, data center modernization, networking, and managed services',
      instruction: 'Use this knowledge base to answer questions about Presidio IT solutions and services, including cloud migration, cybersecurity, AI/ML platforms, data center modernization, networking, collaboration, managed services, and industry-specific implementations.',
      bucketPrefix: 'presidio-kb-docs',
    });

    new cdk.CfnOutput(this, 'BucketName', {
      value: kb.bucket.bucketName,
      exportName: 'PresidioDocsBucketName',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseId', {
      value: kb.knowledgeBase.knowledgeBaseId,
      exportName: 'PresidioKnowledgeBaseId',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseArn', {
      value: kb.knowledgeBase.knowledgeBaseArn,
      exportName: 'PresidioKnowledgeBaseArn',
    });

    this.kbArn = kb.knowledgeBase.knowledgeBaseArn;
  }
}

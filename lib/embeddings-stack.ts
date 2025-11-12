import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';

export interface EmbeddingsStackProps extends cdk.StackProps {
  vpc: ec2.IVpc;
  lambdaSecurityGroup: ec2.ISecurityGroup;
  milvusHost: string;
}

export class EmbeddingsStack extends cdk.Stack {
  public readonly embeddingsFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: EmbeddingsStackProps) {
    super(scope, id, props);

    // Embeddings generator Lambda
    this.embeddingsFunction = new lambda.Function(this, 'EmbeddingsGenerator', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('lambda/embeddings-generator'),
      timeout: cdk.Duration.minutes(5), // Large documents may take time
      memorySize: 1024, // More memory for PDF processing
      vpc: props.vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [props.lambdaSecurityGroup],
      environment: {
        MILVUS_HOST: props.milvusHost,
        MILVUS_PORT: '19530',
      },
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    // Bedrock permissions for Titan Embeddings v2
    this.embeddingsFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['bedrock:InvokeModel'],
      resources: [
        `arn:aws:bedrock:${this.region}::foundation-model/amazon.titan-embed-text-v2:0`
      ],
    }));

    // S3 read permissions for document downloads
    this.embeddingsFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:ListBucket',
      ],
      resources: ['*'], // TODO: Restrict to specific buckets when known
    }));

    // Outputs
    new cdk.CfnOutput(this, 'EmbeddingsFunctionName', {
      value: this.embeddingsFunction.functionName,
      description: 'Lambda function for generating embeddings',
    });

    new cdk.CfnOutput(this, 'EmbeddingsFunctionArn', {
      value: this.embeddingsFunction.functionArn,
      description: 'ARN of embeddings generator Lambda',
    });
  }
}

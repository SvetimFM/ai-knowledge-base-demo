import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export interface RagStackProps extends cdk.StackProps {
  vpc: ec2.IVpc;
  lambdaSecurityGroup: ec2.ISecurityGroup;
  milvusEndpoint: string;
}

export class RagStack extends cdk.Stack {
  public readonly queryFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: RagStackProps) {
    super(scope, id, props);

    // RAG Query Lambda Function
    this.queryFunction = new lambda.Function(this, 'RagQueryFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset('lambda/rag-query'),
      timeout: cdk.Duration.seconds(120),  // Allow time for LLM generation
      memorySize: 1024,  // 1GB for pymilvus + boto3 + LLM context
      vpc: props.vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [props.lambdaSecurityGroup],
      environment: {
        MILVUS_HOST: props.milvusEndpoint,
        MILVUS_PORT: '19530',
        // AWS_REGION is automatically set by Lambda runtime
      },
      logRetention: logs.RetentionDays.ONE_WEEK,
      reservedConcurrentExecutions: 10,  // Limit concurrent queries
    });

    // Bedrock permissions for LLM inference
    this.queryFunction.addToRolePolicy(new iam.PolicyStatement({
      actions: [
        'bedrock:InvokeModel',
        'bedrock:InvokeModelWithResponseStream',
      ],
      resources: [
        // Claude 3.5 Sonnet
        `arn:aws:bedrock:${this.region}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0`,
        // Claude 3 Haiku (fallback)
        `arn:aws:bedrock:${this.region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0`,
        // Titan Embeddings v2
        `arn:aws:bedrock:${this.region}::foundation-model/amazon.titan-embed-text-v2:0`,
      ],
    }));

    // Outputs
    new cdk.CfnOutput(this, 'RagQueryFunctionName', {
      value: this.queryFunction.functionName,
      description: 'RAG Query Lambda function name',
    });

    new cdk.CfnOutput(this, 'RagQueryFunctionArn', {
      value: this.queryFunction.functionArn,
      description: 'RAG Query Lambda function ARN',
    });
  }
}

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';

export interface ApiStackProps extends cdk.StackProps {
  ragQueryFunction: lambda.IFunction;
}

export class ApiStack extends cdk.Stack {
  public readonly api: apigateway.RestApi;
  public readonly apiUrl: string;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    // API Gateway REST API
    this.api = new apigateway.RestApi(this, 'RagApi', {
      restApiName: 'RAG Query API',
      description: 'Public API for RAG question answering',
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 10,  // 10 requests per second
        throttlingBurstLimit: 20,  // 20 concurrent requests
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
      },
      cloudWatchRole: true,
    });

    // Lambda integration
    const lambdaIntegration = new apigateway.LambdaIntegration(
      props.ragQueryFunction,
      {
        proxy: true,  // Pass all request data to Lambda
        integrationResponses: [
          {
            statusCode: '200',
            responseParameters: {
              'method.response.header.Access-Control-Allow-Origin': "'*'",
            },
          },
        ],
      }
    );

    // /query endpoint
    const query = this.api.root.addResource('query');
    query.addMethod('POST', lambdaIntegration, {
      methodResponses: [
        {
          statusCode: '200',
          responseParameters: {
            'method.response.header.Access-Control-Allow-Origin': true,
          },
        },
      ],
    });

    // /health endpoint for monitoring
    const health = this.api.root.addResource('health');
    health.addMethod('GET', new apigateway.MockIntegration({
      integrationResponses: [
        {
          statusCode: '200',
          responseTemplates: {
            'application/json': '{"status":"healthy","timestamp":"$context.requestTime"}',
          },
        },
      ],
      requestTemplates: {
        'application/json': '{"statusCode": 200}',
      },
    }), {
      methodResponses: [{ statusCode: '200' }],
    });

    // Store API URL for output
    this.apiUrl = this.api.url;

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: this.api.url,
      description: 'RAG Query API URL',
      exportName: 'RagApiUrl',
    });

    new cdk.CfnOutput(this, 'ApiId', {
      value: this.api.restApiId,
      description: 'API Gateway REST API ID',
    });

    new cdk.CfnOutput(this, 'QueryEndpoint', {
      value: `${this.api.url}query`,
      description: 'POST endpoint for RAG queries',
    });

    new cdk.CfnOutput(this, 'HealthEndpoint', {
      value: `${this.api.url}health`,
      description: 'GET endpoint for health checks',
    });
  }
}

#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MilvusStack } from '../lib/milvus-stack';
import { EmbeddingsStack } from '../lib/embeddings-stack';
import { IngestionStack } from '../lib/ingestion-stack';
import { RagStack } from '../lib/rag-stack';
import { AuthStack } from '../lib/auth-stack';
import { ApiStack } from '../lib/api-stack';
import { MCPRemoteStack } from '../lib/mcp-remote-stack';
import { MCPApiStack } from '../lib/mcp-api-stack';
import { SecurityStack } from '../lib/security-stack';
import { WAFStack } from '../lib/waf-stack';
import { MigrationStack } from '../lib/migration-stack';
import { getConfig, validateConfig } from '../config/deployment-config';

const app = new cdk.App();

// Load and validate deployment configuration
const config = getConfig();
validateConfig(config);

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
};

// Milvus Vector Database Stack (ECS Fargate + Lambda)
const milvusStack = new MilvusStack(app, 'MilvusStack', {
  env,
  config,
  description: 'Milvus vector database on ECS Fargate with Lambda query access',
});

// Embeddings Generation Stack (Bedrock Titan v2 + Milvus insertion)
const embeddingsStack = new EmbeddingsStack(app, 'EmbeddingsStack', {
  env,
  config,
  vpc: milvusStack.vpc,
  lambdaSecurityGroup: milvusStack.lambdaSecurityGroup,
  milvusHost: milvusStack.milvusEndpoint,
  description: 'Embeddings generation using Bedrock Titan v2 with Milvus storage',
});

// Document Ingestion Stack (S3 + SQS + DynamoDB + Lambda orchestration)
new IngestionStack(app, 'IngestionStack', {
  env,
  config,
  embeddingsFunctionArn: embeddingsStack.embeddingsFunction.functionArn,
  description: 'Document ingestion pipeline with S3, SQS, and state tracking',
});

// RAG Query Stack (Question answering with HyDE + LLM)
const ragStack = new RagStack(app, 'RagStack', {
  env,
  config,
  vpc: milvusStack.vpc,
  lambdaSecurityGroup: milvusStack.lambdaSecurityGroup,
  milvusEndpoint: milvusStack.milvusEndpoint,
  description: 'RAG query pipeline with HyDE retrieval and Claude 3.5 Sonnet',
});

// Migration Stack (One-time partition migration)
new MigrationStack(app, 'MigrationStack', {
  env,
  vpc: milvusStack.vpc,
  lambdaSecurityGroup: milvusStack.lambdaSecurityGroup,
  milvusHost: milvusStack.milvusEndpoint,
  description: 'One-time partition migration Lambda (delete after use)',
});

// Authentication Stack (Cognito User Pool + SES)
const authStack = new AuthStack(app, 'AuthStack', {
  env,
  config,
  description: 'Cognito user authentication with optional SES email',
});

// API Gateway Stack (Public HTTP endpoint with Cognito authentication)
new ApiStack(app, 'ApiStack', {
  env,
  ragQueryFunction: ragStack.queryFunction,
  userPool: authStack.userPool,
  description: 'Protected API Gateway for RAG query access',
});

// MCP Remote Server Stack (Secure Claude Desktop integration)
const mcpRemoteStack = new MCPRemoteStack(app, 'MCPRemoteStack', {
  env,
  config,
  userPool: authStack.userPool,
  userPoolClient: authStack.userPoolClient,
  ragQueryFunction: ragStack.queryFunction,
  description: 'MCP remote server for secure Claude Desktop integration with JWT auth',
});

// MCP API Gateway Stack (HTTP API with Cognito authorization for defense-in-depth)
const mcpApiStack = new MCPApiStack(app, 'MCPApiStack', {
  env,
  mcpStreamHandler: mcpRemoteStack.mcpStreamHandler,
  userPool: authStack.userPool,
  userPoolClient: authStack.userPoolClient,
  description: 'API Gateway for MCP with Cognito auth - replaces direct Lambda Function URL',
});

// Security Stack (CloudTrail for audit logging)
new SecurityStack(app, 'SecurityStack', {
  env,
  description: 'CloudTrail API activity logging with 90-day retention',
});

// WAF Stack (Rate limiting and basic threat protection)
new WAFStack(app, 'WAFStack', {
  env,
  mcpApiId: mcpApiStack.apiId,
  mcpApiArn: mcpApiStack.apiArn,
  description: 'WAF with rate limiting (100 req/5min) for cost protection',
});

// NOTE: Previous KB stacks (HPC, Presidio, TicketTriage) have been removed
// To redeploy them, uncomment the imports and stack declarations above

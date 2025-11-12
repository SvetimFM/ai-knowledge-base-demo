#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MilvusStack } from '../lib/milvus-stack';
import { EmbeddingsStack } from '../lib/embeddings-stack';
import { IngestionStack } from '../lib/ingestion-stack';
import { RagStack } from '../lib/rag-stack';
import { AuthStack } from '../lib/auth-stack';
import { ApiStack } from '../lib/api-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: 'us-east-1'
};

// Milvus Vector Database Stack (ECS Fargate + Lambda)
const milvusStack = new MilvusStack(app, 'MilvusStack', {
  env,
  description: 'Milvus vector database on ECS Fargate with Lambda query access',
});

// Embeddings Generation Stack (Bedrock Titan v2 + Milvus insertion)
const embeddingsStack = new EmbeddingsStack(app, 'EmbeddingsStack', {
  env,
  vpc: milvusStack.vpc,
  lambdaSecurityGroup: milvusStack.lambdaSecurityGroup,
  milvusHost: milvusStack.milvusEndpoint,
  description: 'Embeddings generation using Bedrock Titan v2 with Milvus storage',
});

// Document Ingestion Stack (S3 + SQS + DynamoDB + Lambda orchestration)
new IngestionStack(app, 'IngestionStack', {
  env,
  embeddingsFunctionArn: embeddingsStack.embeddingsFunction.functionArn,
  description: 'Document ingestion pipeline with S3, SQS, and state tracking',
});

// RAG Query Stack (Question answering with HyDE + LLM)
const ragStack = new RagStack(app, 'RagStack', {
  env,
  vpc: milvusStack.vpc,
  lambdaSecurityGroup: milvusStack.lambdaSecurityGroup,
  milvusEndpoint: milvusStack.milvusEndpoint,
  description: 'RAG query pipeline with HyDE retrieval and Claude 3.5 Sonnet',
});

// Authentication Stack (Cognito User Pool + SES)
const authStack = new AuthStack(app, 'AuthStack', {
  env,
  description: 'Cognito user authentication with optional SES email',
});

// API Gateway Stack (Public HTTP endpoint with Cognito authentication)
new ApiStack(app, 'ApiStack', {
  env,
  ragQueryFunction: ragStack.queryFunction,
  userPool: authStack.userPool,
  description: 'Protected API Gateway for RAG query access',
});

// NOTE: Previous KB stacks (HPC, Presidio, TicketTriage) have been removed
// To redeploy them, uncomment the imports and stack declarations above

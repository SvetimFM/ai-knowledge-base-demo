#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MilvusStack } from '../lib/milvus-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: 'us-east-1'
};

// Milvus Vector Database Stack (ECS Fargate + Lambda)
new MilvusStack(app, 'MilvusStack', {
  env,
  description: 'Milvus vector database on ECS Fargate with Lambda query access',
});

// NOTE: Previous KB stacks (HPC, Presidio, TicketTriage) have been removed
// To redeploy them, uncomment the imports and stack declarations above

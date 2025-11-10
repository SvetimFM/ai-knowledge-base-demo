#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { QTicketTriageStack } from '../lib/q_ticket_triage-stack';

const app = new cdk.App();
new QTicketTriageStack(app, 'HpcKnowledgeBaseStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-east-1'
  },
  description: 'Amazon Q + MCP Knowledge Base Demo for HPC Computing (NCCL/RCCL/CUDA)',
});
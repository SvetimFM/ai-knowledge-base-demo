#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { HpcKnowledgeBaseStack } from '../lib/hpc-kb-stack';
import { PresidioKnowledgeBaseStack } from '../lib/presidio-kb-stack';
import { TicketTriageStack } from '../lib/ticket-triage-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
};

const hpcKbStack = new HpcKnowledgeBaseStack(app, 'HpcKnowledgeBaseStack', {
  env,
  description: 'HPC Computing Knowledge Base for MCP and ticket triage',
});

const presidioKbStack = new PresidioKnowledgeBaseStack(app, 'PresidioKnowledgeBaseStack', {
  env,
  description: 'Presidio IT Solutions Knowledge Base for MCP',
});

new TicketTriageStack(app, 'TicketTriageStack', {
  env,
  description: 'Automated ticket triage system using HPC and Presidio knowledge bases',
  hpcKbArn: hpcKbStack.kbArn,
  presidioKbArn: presidioKbStack.kbArn,
});

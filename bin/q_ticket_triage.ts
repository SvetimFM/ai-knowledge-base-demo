#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { QTicketTriageStack } from '../lib/q_ticket_triage-stack';
import { PresidioKnowledgeBaseStack } from '../lib/presidio-kb-stack';

const app = new cdk.App();

// Presidio Knowledge Base Stack (independent)
const presidioStack = new PresidioKnowledgeBaseStack(app, 'PresidioKnowledgeBaseStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-east-1'
  },
  description: 'Presidio IT Solutions Knowledge Base for MCP',
});

// HPC Knowledge Base + Ticket Triage Stack
new QTicketTriageStack(app, 'HpcKnowledgeBaseStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-east-1'
  },
  description: 'HPC Knowledge Base + Ticket Triage System with MCP',
  presidioKbArn: presidioStack.presidioKbArn, // Pass Presidio KB ARN for Lambda permissions
});
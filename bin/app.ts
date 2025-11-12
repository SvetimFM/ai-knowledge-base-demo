#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { HpcKnowledgeBaseStack } from '../lib/hpc-kb-stack';
import { PresidioKnowledgeBaseStack } from '../lib/presidio-kb-stack';
import { TicketTriageStack } from '../lib/ticket-triage-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: 'us-east-1'
};

// Stack 1: HPC Knowledge Base
const hpcKbStack = new HpcKnowledgeBaseStack(app, 'HpcKnowledgeBaseStack', {
  env,
  description: 'HPC Computing Knowledge Base for MCP and ticket triage',
});

// Stack 2: Presidio Knowledge Base
const presidioKbStack = new PresidioKnowledgeBaseStack(app, 'PresidioKnowledgeBaseStack', {
  env,
  description: 'Presidio IT Solutions Knowledge Base for MCP',
});

// Stack 3: Ticket Triage System
new TicketTriageStack(app, 'TicketTriageStack', {
  env,
  description: 'Automated ticket triage system using HPC and Presidio knowledge bases',
  hpcKbArn: hpcKbStack.hpcKbArn,           // Required: HPC KB for triage
  presidioKbArn: presidioKbStack.presidioKbArn,  // Optional: Presidio KB for cross-domain queries
});

import * as cdk from 'aws-cdk-lib';
import { HpcKnowledgeBaseStack } from '../lib/hpc-kb-stack';
import { PresidioKnowledgeBaseStack } from '../lib/presidio-kb-stack';
import { TicketTriageStack } from '../lib/ticket-triage-stack';

describe('Stack Instantiation', () => {
  test('HPC Knowledge Base stack can be instantiated', () => {
    const app = new cdk.App();
    expect(() => {
      new HpcKnowledgeBaseStack(app, 'TestHpcStack');
    }).not.toThrow();
  });

  test('Presidio Knowledge Base stack can be instantiated', () => {
    const app = new cdk.App();
    expect(() => {
      new PresidioKnowledgeBaseStack(app, 'TestPresidioStack');
    }).not.toThrow();
  });

  test('Ticket Triage Stack can be instantiated with KB ARN', () => {
    const app = new cdk.App();
    const hpcStack = new HpcKnowledgeBaseStack(app, 'TestHpcStack');
    expect(() => {
      new TicketTriageStack(app, 'TestTriageStack', {
        hpcKbArn: hpcStack.kbArn,
      });
    }).not.toThrow();
  });

  test('Ticket Triage Stack accepts optional Presidio KB ARN', () => {
    const app = new cdk.App();
    const hpcStack = new HpcKnowledgeBaseStack(app, 'TestHpcStack');
    const presidioStack = new PresidioKnowledgeBaseStack(app, 'TestPresidioStack');
    expect(() => {
      new TicketTriageStack(app, 'TestTriageStack', {
        hpcKbArn: hpcStack.kbArn,
        presidioKbArn: presidioStack.kbArn,
      });
    }).not.toThrow();
  });
});

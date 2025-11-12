import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as ses from 'aws-cdk-lib/aws-ses';

export class AuthStack extends cdk.Stack {
  public readonly userPool: cognito.UserPool;
  public readonly userPoolClient: cognito.UserPoolClient;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Get optional verified email domain from environment
    const verifiedEmailDomain = process.env.VERIFIED_EMAIL_DOMAIN;

    // Configure email settings based on whether we have a verified domain
    let emailConfig: cognito.EmailSettings | undefined;

    if (verifiedEmailDomain) {
      // Use SES with custom domain (requires domain verification in SES)
      console.log(`Using SES with domain: ${verifiedEmailDomain}`);

      emailConfig = {
        from: `noreply@${verifiedEmailDomain}`,
        replyTo: `support@${verifiedEmailDomain}`,
      };
    } else {
      // Use Cognito default email (no SES setup required)
      console.log('Using Cognito default email service');
      emailConfig = undefined;  // Cognito will use default no-reply@verificationemail.com
    }

    // Cognito User Pool
    this.userPool = new cognito.UserPool(this, 'RagUserPool', {
      userPoolName: 'rag-query-users',
      selfSignUpEnabled: true,
      signInAliases: {
        email: true,
        username: false,
      },
      autoVerify: {
        email: true,
      },
      email: verifiedEmailDomain
        ? cognito.UserPoolEmail.withSES({
            fromEmail: `noreply@${verifiedEmailDomain}`,
            fromName: 'RAG Query System',
            replyTo: `support@${verifiedEmailDomain}`,
          })
        : cognito.UserPoolEmail.withCognito(),  // Default Cognito email
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: true,
        tempPasswordValidity: cdk.Duration.days(3),
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      mfa: cognito.Mfa.OPTIONAL,
      mfaSecondFactor: {
        sms: false,
        otp: true,  // Time-based one-time password (TOTP)
      },
      userVerification: {
        emailSubject: 'Verify your RAG Query account',
        emailBody: 'Thanks for signing up! Your verification code is {####}',
        emailStyle: cognito.VerificationEmailStyle.CODE,
      },
      removalPolicy: cdk.RemovalPolicy.RETAIN,  // Don't delete users on stack deletion
    });

    // User Pool Client (for application authentication)
    this.userPoolClient = new cognito.UserPoolClient(this, 'RagUserPoolClient', {
      userPool: this.userPool,
      userPoolClientName: 'rag-query-client',
      authFlows: {
        userPassword: true,
        userSrp: true,  // Secure Remote Password
        custom: false,
        adminUserPassword: false,
      },
      generateSecret: false,  // Public client (no secret needed for user auth)
      refreshTokenValidity: cdk.Duration.days(30),
      accessTokenValidity: cdk.Duration.hours(1),
      idTokenValidity: cdk.Duration.hours(1),
      enableTokenRevocation: true,
      preventUserExistenceErrors: true,  // Security: don't reveal if user exists
    });

    // Outputs
    new cdk.CfnOutput(this, 'UserPoolId', {
      value: this.userPool.userPoolId,
      description: 'Cognito User Pool ID',
      exportName: 'RagUserPoolId',
    });

    new cdk.CfnOutput(this, 'UserPoolArn', {
      value: this.userPool.userPoolArn,
      description: 'Cognito User Pool ARN',
    });

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: this.userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
      exportName: 'RagUserPoolClientId',
    });

    new cdk.CfnOutput(this, 'CognitoSignUpCommand', {
      value: `aws cognito-idp sign-up --client-id ${this.userPoolClient.userPoolClientId} --username user@example.com --password 'YourSecurePassword123!'`,
      description: 'Example: Sign up a new user',
    });

    new cdk.CfnOutput(this, 'CognitoSignInCommand', {
      value: `aws cognito-idp initiate-auth --client-id ${this.userPoolClient.userPoolClientId} --auth-flow USER_PASSWORD_AUTH --auth-parameters USERNAME=user@example.com,PASSWORD='YourSecurePassword123!'`,
      description: 'Example: Sign in to get tokens',
    });

    if (verifiedEmailDomain) {
      new cdk.CfnOutput(this, 'EmailDomain', {
        value: verifiedEmailDomain,
        description: 'SES verified email domain',
      });

      new cdk.CfnOutput(this, 'SESSetupInstructions', {
        value: `Verify domain in SES: aws ses verify-domain-identity --domain ${verifiedEmailDomain}`,
        description: 'SES domain verification command',
      });
    } else {
      new cdk.CfnOutput(this, 'EmailProvider', {
        value: 'Cognito Default (no-reply@verificationemail.com)',
        description: 'Using Cognito default email service',
      });
    }
  }
}

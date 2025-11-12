import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as servicediscovery from 'aws-cdk-lib/aws-servicediscovery';

export class MilvusStack extends cdk.Stack {
  public readonly queryFunction: lambda.Function;
  public readonly milvusEndpoint: string;
  public readonly vpc: ec2.IVpc;
  public readonly lambdaSecurityGroup: ec2.ISecurityGroup;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC with private and public subnets
    const vpc = new ec2.Vpc(this, 'MilvusVpc', {
      maxAzs: 2,
      natGateways: 1, // Required for ECS to pull Docker images
      subnetConfiguration: [
        {
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
      ],
    });

    // Security group for ECS (Milvus)
    const ecsSg = new ec2.SecurityGroup(this, 'MilvusEcsSg', {
      vpc,
      description: 'Security group for Milvus ECS tasks',
      allowAllOutbound: true,
    });

    // Security group for Lambda
    const lambdaSg = new ec2.SecurityGroup(this, 'MilvusLambdaSg', {
      vpc,
      description: 'Security group for Lambda functions accessing Milvus',
      allowAllOutbound: true,
    });

    // Allow Lambda to connect to Milvus on port 19530
    ecsSg.addIngressRule(
      lambdaSg,
      ec2.Port.tcp(19530),
      'Allow Lambda to access Milvus'
    );

    // EFS filesystem for Milvus data persistence
    const fileSystem = new efs.FileSystem(this, 'MilvusFileSystem', {
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      lifecyclePolicy: efs.LifecyclePolicy.AFTER_7_DAYS,
      performanceMode: efs.PerformanceMode.GENERAL_PURPOSE,
      throughputMode: efs.ThroughputMode.BURSTING,
    });

    // Allow ECS to access EFS
    fileSystem.connections.allowFrom(ecsSg, ec2.Port.tcp(2049));

    // EFS Access Point for Milvus
    const accessPoint = fileSystem.addAccessPoint('MilvusAccessPoint', {
      path: '/milvus',
      createAcl: {
        ownerGid: '1000',
        ownerUid: '1000',
        permissions: '755',
      },
      posixUser: {
        gid: '1000',
        uid: '1000',
      },
    });

    // ECS Cluster
    const cluster = new ecs.Cluster(this, 'MilvusCluster', {
      vpc,
      clusterName: 'milvus-cluster',
    });

    // Fargate Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'MilvusTaskDef', {
      memoryLimitMiB: 1024,
      cpu: 512,
      volumes: [
        {
          name: 'milvus-data',
          efsVolumeConfiguration: {
            fileSystemId: fileSystem.fileSystemId,
            transitEncryption: 'ENABLED',
            authorizationConfig: {
              accessPointId: accessPoint.accessPointId,
              iam: 'ENABLED',
            },
          },
        },
      ],
    });

    // Milvus container
    const milvusContainer = taskDefinition.addContainer('milvus', {
      image: ecs.ContainerImage.fromRegistry('milvusdb/milvus:latest'),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'milvus',
        logRetention: logs.RetentionDays.ONE_WEEK,
      }),
      environment: {
        ETCD_USE_EMBED: 'true',
        COMMON_STORAGETYPE: 'local',
      },
      portMappings: [
        {
          containerPort: 19530,
          protocol: ecs.Protocol.TCP,
        },
      ],
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:9091/healthz || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
        startPeriod: cdk.Duration.seconds(60),
      },
    });

    // Mount EFS volume
    milvusContainer.addMountPoints({
      sourceVolume: 'milvus-data',
      containerPath: '/var/lib/milvus',
      readOnly: false,
    });

    // AWS Cloud Map - Private DNS Namespace for service discovery
    const namespace = new servicediscovery.PrivateDnsNamespace(this, 'MilvusNamespace', {
      vpc,
      name: 'milvus.local',
      description: 'Private DNS namespace for Milvus service discovery',
    });

    // ECS Fargate Service with Cloud Map integration
    const service = new ecs.FargateService(this, 'MilvusService', {
      cluster,
      taskDefinition,
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [ecsSg],
      enableExecuteCommand: true, // For debugging
      cloudMapOptions: {
        name: 'milvus',
        cloudMapNamespace: namespace,
        dnsRecordType: servicediscovery.DnsRecordType.A,
        dnsTtl: cdk.Duration.seconds(10),
      },
    });

    // Resolvable DNS endpoint for Lambda (now actually works!)
    this.milvusEndpoint = 'milvus.milvus.local';

    // Lambda function to query Milvus
    this.queryFunction = new lambda.Function(this, 'MilvusQueryFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.query',
      code: lambda.Code.fromAsset('lambda/milvus-query'),
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [lambdaSg],
      environment: {
        MILVUS_HOST: this.milvusEndpoint,
        MILVUS_PORT: '19530',
      },
      logRetention: logs.RetentionDays.ONE_WEEK,
    });

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', {
      value: vpc.vpcId,
      description: 'VPC ID',
    });

    new cdk.CfnOutput(this, 'ClusterName', {
      value: cluster.clusterName,
      description: 'ECS Cluster name',
    });

    new cdk.CfnOutput(this, 'ServiceName', {
      value: service.serviceName,
      description: 'ECS Service name',
    });

    new cdk.CfnOutput(this, 'QueryFunctionName', {
      value: this.queryFunction.functionName,
      description: 'Lambda function for querying Milvus',
    });

    new cdk.CfnOutput(this, 'MilvusEndpoint', {
      value: this.milvusEndpoint,
      description: 'Milvus connection endpoint for Lambda',
    });

    // Export for embeddings stack
    this.vpc = vpc;
    this.lambdaSecurityGroup = lambdaSg;
  }
}

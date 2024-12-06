import aws_cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
from constructs import Construct


class VectorDB(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        init_script = ec2.CloudFormationInit.from_elements(
            ec2.InitCommand.shell_command("yum update -y"),
            ec2.InitCommand.shell_command("yum install docker -y "),
            ec2.InitCommand.shell_command("service docker start"),
            ec2.InitCommand.shell_command("usermod -a -G docker ec2-user"),
            ec2.InitCommand.shell_command(
                """docker run \
                -d \
                -p 6333:6333 \
                -p 6334:6334 \
                -v $(pwd)/qdrant_storage:/qdrant/storage \
                qdrant/qdrant:v0.11.4"""
            ),
        )

        self.qdrant = ec2.Instance(
            self,
            "qdrant",
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.T3,
                instance_size=ec2.InstanceSize.MEDIUM,
            ),
            machine_image=ec2.AmazonLinuxImage(),
            init=init_script,
            init_options=ec2.ApplyCloudFormationInitOptions(ignore_failures=True),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            vpc=vpc,
            user_data_causes_replacement=True,
        )

        self.qdrant.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess"),
        )

        aws_cdk.CfnOutput(self, "QDRANT_HOST", value=self.qdrant.instance_private_ip)

    def allow_qdrant_access(
        self,
        resource: ec2.IConnectable,
        allow_http: bool = True,
        allow_grpc: bool = True,
    ):
        if allow_http:
            self.qdrant.connections.allow_from(
                resource,
                ec2.Port.tcp(6333),
                "Allow QDrant HTTP ingress from bastion host.",
            )
        if allow_grpc:
            self.qdrant.connections.allow_from(
                resource,
                ec2.Port.tcp(6334),
                "Allow QDrant GRPC ingress from bastion host.",
            )

    @property
    def qdrant_host(self):
        return self.qdrant.instance_private_ip

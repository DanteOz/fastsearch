from aws_cdk import aws_apprunner_alpha as apprunner
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as assets
from aws_cdk.aws_apprunner import CfnService
from constructs import Construct

from infra.backend.utils import load_env_vars
from infra.constants import BACKEND_DIR, PROJECT_DIR


class Backend(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, vector_db: Construct, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        env_path = PROJECT_DIR / ".env.template"
        env = load_env_vars(env_path)

        build_args = ["HF_TOKEN", "RETRIEVER_MODEL", "RANKING_MODEL"]
        asset = assets.DockerImageAsset(
            self,
            "BackendImage",
            directory=str(BACKEND_DIR),
            build_args={key: env[key] for key in build_args},
            platform=assets.Platform.LINUX_AMD64,
        )

        # Only use VPC Connector when self-hosting qdrant
        if vpc is None and vector_db is None:
            vpc_connector = None
        else:
            vpc_connector = apprunner.VpcConnector(
                self,
                "VpcConnector",
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            )

        self.backend = apprunner.Service(
            self,
            "Service",
            source=apprunner.Source.from_asset(
                asset=asset,
                image_configuration=apprunner.ImageConfiguration(port=80, environment_variables=env),
            ),
            cpu=apprunner.Cpu.FOUR_VCPU,
            memory=apprunner.Memory.EIGHT_GB,
            vpc_connector=vpc_connector,
        )

        cfn_backend = self.backend.node.default_child
        cfn_backend.health_check_configuration = CfnService.HealthCheckConfigurationProperty(
            healthy_threshold=1,
            interval=1,
            path="/",
            protocol="HTTP",
            timeout=1,
            unhealthy_threshold=1,
        )

        if vector_db is not None:
            vector_db.allow_qdrant_access(vpc_connector.connections)

    @property
    def origin(self):
        return origins.HttpOrigin(self.backend.service_url)

from pathlib import Path

from aws_cdk import aws_autoscaling as autoscale
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from constructs import Construct

from infra.backend.utils import load_env_vars


class Backend(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.IVpc = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cluster: ecs.Cluster = ecs.Cluster(self, "backend-cluster", vpc=vpc)

        # Definie EC2 Auto Scaling Group
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_autoscaling/README.html
        scaling_group = autoscale.AutoScalingGroup(
            self,
            "scaling-group",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.C6I,
                instance_size=ec2.InstanceSize.XLARGE,
            ),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            desired_capacity=1,
            min_capacity=1,
            max_capacity=10,
        )

        # Add AutoScaling Group as cluster capacity provider
        capacity_provider = ecs.AsgCapacityProvider(self, "cap-provider", auto_scaling_group=scaling_group)
        cluster.add_asg_capacity_provider(capacity_provider)

        # Define Docker Image
        env_path = Path(__file__).parent.parent.parent.joinpath(".env.template").absolute()
        env = load_env_vars(env_path)

        build_args = ["HF_TOKEN", "RETRIEVER_MODEL", "RANKING_MODEL"]
        asset = assets.DockerImageAsset(
            self,
            "BackendImage",
            directory=str(Path(__file__).parent.parent.parent.joinpath("backend").absolute()),
            build_args={key: env[key] for key in build_args},
            platform=assets.Platform.LINUX_AMD64,
        )
        image = ecs.ContainerImage.from_docker_image_asset(asset)

        # Define backend task
        task: ecs.Ec2TaskDefinition = ecs.Ec2TaskDefinition(
            self, "backend-task", network_mode=ecs.NetworkMode.BRIDGE
        )

        # Add Docker container definition
        container = task.add_container(
            "backend-container",
            image=image,
            cpu=4,
            environment=env,
            memory_limit_mib=4096,
            port_mappings=[
                ecs.PortMapping(
                    name="backend-port",
                    container_port=80,
                    app_protocol=ecs.AppProtocol.http,
                )
            ],
        )

        # Create ECS service
        service: ecs.Ec2Service = ecs.Ec2Service(self, "service", cluster=cluster, task_definition=task)

        # Define Load Balancer
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/README.html#include-an-application-network-load-balancer
        lb: elbv2.ApplicationLoadBalancer = elbv2.ApplicationLoadBalancer(
            self, "lb", vpc=vpc, internet_facing=True
        )
        listener = lb.add_listener("listener", port=80, protocol=elbv2.ApplicationProtocol.HTTP)
        target_group = listener.add_targets(
            "backend_group",
            port=80,
            targets=[
                service.load_balancer_target(
                    container_name=container.container_name,
                    container_port=container.container_port,
                    protocol=ecs.Protocol.TCP,
                )
            ],
        )

        # Define service scaling policy
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/README.html#task-auto-scaling
        scaling_policy = service.auto_scale_task_count(max_capacity=10)
        scaling_policy.scale_on_request_count(
            "RequestScaling", requests_per_target=200, target_group=target_group
        )

import os

from aws_cdk import Duration, Stack
from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as sm
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()

if os.environ.get("DEV_OR_PROD") == "prod":
    certificate_arn = "arn:aws:acm:us-east-1:614871946825:certificate/6f66a681-ce7a-4d57-afbc-cfdbca17972e"
else:
    certificate_arn = "arn:aws:acm:us-east-1:614871946825:certificate/af060bf9-a5c1-4084-9990-9ba26da84bc1"

jwt_secret_arn = (
    "arn:aws:secretsmanager:us-east-1:614871946825:secret:supabase-jwt-secret-cnJpRy"
)

wedatanation_avatar_table = (
    "wedatanation-avatar"
    if os.environ.get("DEV_OR_PROD") == "prod"
    else "wedatanation-avatar-dev"
)


class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC and Subnets for the ECS Cluster
        vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=2,
        )

        # Create middleware ecs cluster
        image = ecs.ContainerImage.from_asset(
            directory=".",
            build_args={"platform": "linux/amd64"},
        )

        role = iam.Role(
            self,
            "FargateContainerRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        certificate = certificatemanager.Certificate.from_certificate_arn(
            self, "pollinationsworker", certificate_arn
        )

        # Create ECS pattern for the ECS Cluster
        cluster = ecs_patterns.ApplicationLoadBalancedFargateService(  # noqa
            self,
            "pollen-rest-api",
            vpc=vpc,
            public_load_balancer=True,
            protocol=elb.ApplicationProtocol.HTTPS,
            certificate=certificate,
            redirect_http=True,
            desired_count=2,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=5000,
                environment={
                    "DEBUG": "True",
                    "LOG_LEVEL": "DEBUG",
                    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "wedatanation_avatar_table": wedatanation_avatar_table,
                    "SUPABASE_API_KEY": os.environ.get("SUPABASE_API_KEY"),
                    "SUPABASE_URL": os.environ.get("SUPABASE_URL"),
                    "SUPABASE_ID": os.environ.get("SUPABASE_ID"),
                    "REPLICATE_API_TOKEN": os.environ.get("REPLICATE_API_TOKEN"),
                    "DB_NAME": "pollen"
                    if os.environ.get("DEV_OR_PROD") == "prod"
                    else "pollen_dev",
                },
                secrets={
                    "JWT_SECRET": ecs.Secret.from_secrets_manager(
                        sm.Secret.from_secret_attributes(
                            self,
                            "secret_key",
                            secret_complete_arn=jwt_secret_arn,
                        )
                    )
                },
                # add permission to get SQS queue url and send messages to SQS queue
                task_role=role,
            ),
            idle_timeout=Duration.seconds(4000),
            memory_limit_mib=1024,
            cpu=256,
        )  # noqa: F841

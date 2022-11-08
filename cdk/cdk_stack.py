from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_secretsmanager as sm
from constructs import Construct

certificate_arn = "arn:aws:acm:us-east-1:614871946825:certificate/226b3e6a-612f-449a-ae71-5d45648246f1"
jwt_secret_arn = (
    "arn:aws:secretsmanager:us-east-1:614871946825:secret:supabase-jwt-secret-cnJpRy"
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
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=5000,
                environment={
                    "DEBUG": "True",
                    "LOG_LEVEL": "DEBUG",
                    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
            memory_limit_mib=1024,
            cpu=256,
        )  # noqa: F841

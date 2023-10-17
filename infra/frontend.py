from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy
from constructs import Construct

from infra.constants import FRONTEND_DIR


class StaticOrigin(Construct):
    def __init__(
        self, scope: Construct, id: str, folder: str, index_file: str | None = None, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create S3 Bucket
        self.bucket = s3.Bucket(
            self,
            "bucket",
            website_index_document=index_file,
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
        )

        # Create S3 Deployment
        self.static_assets = s3deploy.Source.asset(folder)

        # Create S3 Origin
        self.origin = origins.S3Origin(self.bucket)

        # Create Behavior Opttions
        self.behavior = cloudfront.BehaviorOptions(
            origin=self.origin,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
            origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,
        )

    def bucket_deployment(self, distribution: cloudfront.Distribution, paths: list[str]) -> None:
        self.deployment = s3deploy.BucketDeployment(
            self,
            "deployment",
            sources=[self.static_assets],
            destination_bucket=self.bucket,
            distribution=distribution,
            distribution_paths=paths,
        )


class Frontend(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        default_root: str = "index.html",
        domain_name: str = None,
        certificate_arn: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        assert domain_name and certificate_arn
        domain_name = None if domain_name is None else [domain_name]
        certificate = (
            None
            if domain_name is None
            else acm.Certificate.from_certificate_arn(self, "certificate", certificate_arn)
        )

        # Create S3 Origins
        self.app = StaticOrigin(self, "app", folder=str(FRONTEND_DIR), index_file=default_root)

        # Create CloudFront Distributions
        self.distribution: cloudfront.Distribution = cloudfront.Distribution(
            self,
            "distribution",
            default_behavior=self.app.behavior,
            default_root_object=default_root,
            domain_names=domain_name,
            certificate=certificate,
        )
        # Create S3 Bucket Deployments
        self.app.bucket_deployment(self.distribution, paths=["/*"])

    def attach_backend(self, origin: cloudfront.OriginBase):
        self.distribution.add_behavior(
            path_pattern="/api/*",
            origin=origin,
            cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
            allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            origin_request_policy=cloudfront.OriginRequestPolicy(
                self,
                "fwd-policy",
                cookie_behavior=cloudfront.OriginRequestCookieBehavior.all(),
                query_string_behavior=cloudfront.OriginRequestQueryStringBehavior.all(),
            ),
        )

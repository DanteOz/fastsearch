import os

import aws_cdk
from constructs import Construct

from infra.backend.core import Backend
from infra.constants import CERTIFICATE_ARN, DOMAIN_NAME
from infra.frontend import Frontend


class FastSearch(aws_cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        frontend = Frontend(self, id="frontend", domain_name=DOMAIN_NAME, certificate_arn=CERTIFICATE_ARN)
        backend = Backend(self, id="backend", vpc=None, vector_db=None)
        frontend.attach_backend(backend.origin)


if __name__ == "__main__":
    app = aws_cdk.App()

    stack = FastSearch(
        app,
        "FastSearch",
        env=aws_cdk.Environment(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"),
            region=os.getenv("CDK_DEFAULT_REGION"),
        ),
    )

    app.synth()

import os
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    domain_name: str
    certificate_arn: str
    project_dir: Path

    @property
    def frontend_dir(self) -> Path:
        return self.project_dir / "frontend" / ".output" / "public"

    @property
    def backend_dir(self) -> Path:
        return self.project_dir / "backend"


config = Config(
    domain_name="fastsearch.danteoz.com",
    certificate_arn=os.getenv("CERTIFICATE_ARN"),
    project_dir=Path(__file__).parent.parent.parent.parent.absolute(),
)

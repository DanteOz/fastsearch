import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.absolute()

FRONTEND_DIR = PROJECT_DIR / "frontend" / ".output" / "public"
DOMAIN_NAME = "fastsearch.danteoz.com"
CERTIFICATE_ARN = os.getenv("CERTIFICATE_ARN")

BACKEND_DIR = PROJECT_DIR / "backend"

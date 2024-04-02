import os
import platform
from pathlib import Path

from sqlalchemy import URL, create_engine

CONNECT_URL = URL.create(
    drivername="postgresql+psycopg",
    host=os.getenv("PGHOST"),
    database=os.getenv("PGDATABASE"),
    username=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    query={"sslmode": "require"},
)


def ssl_cert_path() -> str:
    """Get path to SSL CERTS"""
    if platform.system() == "Linux":
        cert_dir = Path("/etc/ssl/certs/").resolve()
        cert_path = cert_dir.joinpath("ca-certificates.crt")
        bundle_path = cert_dir.joinpath("ca-bundle.crt")
        if cert_path.exists():
            return str(cert_path)
        elif bundle_path.exists():
            return str(bundle_path)
    elif platform.system() == "Darwin":
        return "/etc/ssl/cert.pem"

    raise RuntimeError("Could not find SSL certificate.")


engine = create_engine(
    url=CONNECT_URL,
    # connect_args={"ssl": {"ca": ssl_cert_path()}},
)

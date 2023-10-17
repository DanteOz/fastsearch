import os
from sqlalchemy import create_engine, URL
import platform
from pathlib import Path

CONNECT_URL = URL.create(
    drivername="mysql+mysqldb",
    username=os.getenv("PS_USER"),
    password=os.getenv("PS_PSWD"),
    host=os.getenv("PS_HOST"),
    database=os.getenv("PS_DB"),
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
    connect_args={"ssl": {"ca": ssl_cert_path()}},
)

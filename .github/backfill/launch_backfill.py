# /// script
# requires-python = "==3.10"
# dependencies = [
#     "dagster-graphql==1.9.4",
#     "sshtunnel==0.4.0",
# ]
# ///
import os

from dagster_graphql import DagsterGraphQLClient
from dagster_graphql.client.query import LAUNCH_PARTITION_BACKFILL_MUTATION
from sshtunnel import SSHTunnelForwarder

SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = os.getenv("SSH_PORT")
SSH_USER = os.getenv("SSH_USER")
SSH_KEY = os.getenv("SSH_KEY")
DAGSTER_PORT = os.getenv("DAGSTER_PORT")


def main():
    with SSHTunnelForwarder(
        ssh_address_or_host=SSH_HOST,
        ssh_port=SSH_PORT,
        ssh_username=SSH_USER,
        ssh_pkey=SSH_KEY,
        local_bind_address=DAGSTER_PORT,
        remote_bind_address=DAGSTER_PORT,
    ):
        client = DagsterGraphQLClient("localhost", port_number=DAGSTER_PORT)
        variables = {
            "backfillParams": {
                "assetSelection": [{"path": "embeddings"}, {"path": "vector_index"}],
                "allPartitions": True,
            }
        }
    response = client._execute(LAUNCH_PARTITION_BACKFILL_MUTATION, variables=variables)
    assert response["launchPartitionBackfill"]["__typename"] == "LaunchBackfillSuccess"


if __name__ == "__main__":
    main()

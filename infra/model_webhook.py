import json
import os
import urllib3

USER = os.getenv("GH_USER")
REPO = os.getenv("GH_REPO")
ACCESS_TOKEN = os.getenv("GH_PAT")
SECRET = os.getenv("HF_SECRET")

http = urllib3.PoolManager()


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event["requestContext"]["http"]["path"]
    secret = event["headers"]["x-webhook-secret"]
    if method == "POST" and path == "/" and secret == SECRET:
        payload = json.loads(event["body"])
        data = {
            "event_type": "update_weight",
            "client_payload": {
                "updated_repo": payload["repo"]["name"],
            },
        }
        rsp = http.request(
            "POST",
            f"https://api.github.com/repos/{USER}/{REPO}/dispatches",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"token {ACCESS_TOKEN}",
            },
            body=json.dumps(data).encode("utf-8"),
        )
        assert rsp.status == 204

        return {"statusCode": 204, "body": None}
    else:
        return {"statusCode": 404}

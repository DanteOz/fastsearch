from typing import Optional

from dagster import ConfigurableResource
from qdrant_client import QdrantClient
from upath import UPath

import modal


class HuggingfFaceModel(ConfigurableResource):
    model_id: str


class QdrantDatabase(ConfigurableResource):
    host: str
    key: str
    collection: str

    def create_client(self, grpc: bool = True, https: bool = True, *args, **kwargs):
        return QdrantClient(*args, host=self.host, api_key=self.key, prefer_grpc=grpc, https=https, **kwargs)


class ModalWhispher(ConfigurableResource):
    app_name: Optional[str] = "fastsearch"
    tag: Optional[str] = "transcribe"

    def transcribe(self, path: UPath) -> dict:
        raise Exception()
        transcribe_fn: modal.Function = modal.Function.lookup(self.app_name, self.tag)
        return transcribe_fn.remote(path)


class MockWhispher(ModalWhispher):
    def transcribe(self, path: UPath) -> dict:
        mock_transcript = {
            "text": "DEFAULT",
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 4.8,
                    "text": " All right, I'm Rachel Thomas.",
                    "tokens": [1057, 558, 11, 286, 478, 14246, 8500, 13],
                    "temperature": 0.0,
                    "avg_logprob": -0.1989734539618859,
                    "compression_ratio": 1.5720524017467248,
                    "no_speech_prob": 0.01032023411244154,
                }
            ],
        }
        return mock_transcript

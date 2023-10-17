import os

import dagster
from dagster import Definitions, EnvVar, load_assets_from_modules

from fastpipeline import sensors
from fastpipeline.assets import (
    indexing,
    metadata,
    scraping,
    transcription,
)
from fastpipeline.io_managers import (
    ConfigurableJSONFileSystemIOManager,
    ConfigurablePolarsArrowFileSystemIOManager,
    ConfigurablePydanticFileSystemIOManager,
)
from fastpipeline.resources import (
    HuggingfFaceModel,
    MockWhispher,
    ModalWhispher,
    QdrantDatabase,
)

DAGSTER_ENV = os.getenv("DAGSTER_ENV", "local")

all_assets = [
    *load_assets_from_modules([indexing], group_name="indexing"),
    *load_assets_from_modules([metadata], group_name="metadata"),
    *load_assets_from_modules([scraping], group_name="scraping"),
    *load_assets_from_modules([transcription], group_name="transcription"),
]

if DAGSTER_ENV == "prod":
    qdrant_resource = QdrantDatabase(
        collection=EnvVar("QDRANT_COLLECTION"),
        host=EnvVar("QDRANT_HOST"),
        key=EnvVar("QDRANT_API_KEY"),
    )
    whispher_resource = ModalWhispher()

else:
    qdrant_resource = QdrantDatabase(
        collection="fastai_dev",
        host=EnvVar("QDRANT_HOST"),
        key=EnvVar("QDRANT_API_KEY"),
    )
    whispher_resource = MockWhispher()

resources = {
    "io_manager": dagster.FilesystemIOManager(),
    "polars_io": ConfigurablePolarsArrowFileSystemIOManager(),
    "json_io": ConfigurableJSONFileSystemIOManager(),
    "pydantic_io": ConfigurablePydanticFileSystemIOManager(),
    "embed_config": HuggingfFaceModel(model_id=EnvVar("EMBEDDING_MODEL")),
    "transcription_model": whispher_resource,
    "qdrant": qdrant_resource,
}


defs = Definitions(assets=all_assets, resources=resources, sensors=[sensors.videos_senor])

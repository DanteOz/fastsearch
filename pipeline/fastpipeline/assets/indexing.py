import numpy as np
import polars as pl
import torch
from dagster import AssetExecutionContext, AutoMaterializePolicy, asset
from qdrant_client import models
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from fastpipeline.assets.metadata import Metadata
from fastpipeline.partitions import video_partition_def
from fastpipeline.resources import HuggingfFaceModel, QdrantDatabase


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


@asset(partitions_def=video_partition_def, auto_materialize_policy=AutoMaterializePolicy.eager())
def embeddings(
    context: AssetExecutionContext,
    processed_transcripts: pl.DataFrame,
    embed_config: HuggingfFaceModel,
) -> np.ndarray:
    """Embeddings for lecture transcript segments."""

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModel.from_pretrained(embed_config.model_id).to(device)
    tokenizer = AutoTokenizer.from_pretrained(embed_config.model_id)

    dataloader = torch.utils.data.DataLoader(
        processed_transcripts["text"].to_list(), batch_size=32, shuffle=False
    )

    vectors = []
    with torch.inference_mode():
        for batch in tqdm(dataloader):
            tokens = tokenizer(batch, padding=True, return_tensors="pt", truncation=True).to(device)
            token_embeds = model(**tokens)
            sent_embeds = (
                mean_pooling(
                    token_embeds["last_hidden_state"],
                    tokens["attention_mask"],
                )
                .cpu()
                .numpy()
            )
            vectors.append(sent_embeds)

    return np.vstack(vectors)


@asset(
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
    io_manager_key="polars_io",
)
def payloads(
    context: AssetExecutionContext,
    metadata: Metadata,
    lessons: pl.DataFrame,
    courses: pl.DataFrame,
    processed_transcripts: pl.DataFrame,
) -> pl.DataFrame:
    """JSON payloads for fastsearch search results."""
    payload = (
        processed_transcripts.with_columns(
            [
                pl.lit(metadata.title).alias("title"),
                pl.lit(metadata.thumbnail).alias("thumbnail"),
            ]
        )
        .join(lessons, on="video_id", how="left")
        .join(courses, on="course_id", how="left")
        .select(
            [
                pl.col(["video_id", "text", "start", "thumbnail"]),
                pl.when(pl.col("name").is_not_null())
                .then(pl.col("name"))
                .otherwise(pl.col("title"))
                .alias("title"),
                pl.col("course_url").alias("course"),
                pl.col("lesson_url").alias("lesson"),
                pl.col("forum_url").alias("forum"),
            ]
        )
    )
    return payload


@asset(partitions_def=video_partition_def, auto_materialize_policy=AutoMaterializePolicy.eager())
def vector_index(
    context: AssetExecutionContext,
    embeddings: np.ndarray,
    payloads: pl.DataFrame,
    qdrant: QdrantDatabase,
) -> None:
    """Vector index (qdrant) of fast.ai lecture transcript segments."""
    client = qdrant.create_client()

    existing_collections = [collection.name for collection in client.get_collections().collections]
    if qdrant.collection not in existing_collections:
        context.log.error("COLLECTION DOESN'T EXISIT")
        client.recreate_collection(
            collection_name=qdrant.collection,
            vectors_config=models.VectorParams(size=embeddings.shape[-1], distance=models.Distance.COSINE),
            on_disk_payload=True,
        )
        context.log.info("Created Collection")

    context.log.info("Uploading Collection")
    client.upload_collection(
        collection_name=qdrant.collection,
        vectors=embeddings,
        payload=payloads.to_dicts(),
        batch_size=min(512, len(payloads)),
    )

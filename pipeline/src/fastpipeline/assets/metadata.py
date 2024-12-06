from typing import Optional

import polars as pl
from dagster import AssetExecutionContext, AutoMaterializePolicy, asset
from pydantic import BaseModel

from fastpipeline.assets.constants import SEED_DIR
from fastpipeline.partitions import video_partition_def


@asset(io_manager_key="polars_io", auto_materialize_policy=AutoMaterializePolicy.eager())
def courses() -> pl.DataFrame:
    """Load fast.ai courses seed data."""
    return pl.read_csv(SEED_DIR / "fastai_metadata" / "courses.csv")


@asset(io_manager_key="polars_io", auto_materialize_policy=AutoMaterializePolicy.eager())
def lessons() -> pl.DataFrame:
    """Load fast.ai lessons seed data."""
    return pl.read_csv(SEED_DIR / "fastai_metadata" / "lessons.csv")


class Category(BaseModel):
    video_id: str
    category: str


@asset(
    io_manager_key="pydantic_io",
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def categories(context: AssetExecutionContext, video_metadata: dict) -> list[Category]:
    """Extract and normalize metadata from raw youtube video metadata."""
    video_id = context.partition_key
    categories = (
        [Category(video_id=video_id, category=c) for c in video_metadata["categories"]]
        if "categories" in video_metadata
        else []
    )
    return categories


class Chapter(BaseModel):
    video_id: str
    title: str
    start_time: float
    end_time: float


@asset(
    io_manager_key="pydantic_io",
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def chapters(context: AssetExecutionContext, video_metadata: dict) -> list[Chapter]:
    """Extract and normalize metadata from raw youtube video metadata."""
    video_id = context.partition_key
    chapters = (
        [Chapter(video_id=video_id, **c) for c in video_metadata["chapters"]]
        if "chapters" in video_metadata and video_metadata["chapters"] is not None
        else []
    )
    return chapters


class Subtitle(BaseModel):
    video_id: str
    language: str
    url: str
    ext: str
    name: str
    protocol: Optional[str] = None


@asset(
    io_manager_key="pydantic_io",
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def subtitles(context: AssetExecutionContext, video_metadata: dict) -> list[Subtitle]:
    """Extract and normalize metadata from raw youtube video metadata."""
    video_id = context.partition_key
    subtitles = []
    if (
        "subtitles" in video_metadata
        and video_metadata["subtitles"] is not None
        and len(video_metadata["subtitles"]) > 1
    ):
        for lang in video_metadata["subtitles"]:
            for source in video_metadata["subtitles"][lang]:
                subtitle = Subtitle(video_id=video_id, language=lang, **source)
                subtitles.append(subtitle)
    return subtitles


class Tag(BaseModel):
    video_id: str
    tag: str


@asset(
    io_manager_key="pydantic_io",
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def tags(context: AssetExecutionContext, video_metadata: dict) -> list[Tag]:
    """Extract and normalize metadata from raw youtube video metadata."""
    video_id = context.partition_key
    tags = (
        [Tag(video_id=video_id, tag=tag) for tag in video_metadata["tags"]]
        if "tags" in video_metadata and video_metadata["tags"] is not None
        else []
    )
    return tags


class Thumbnail(BaseModel):
    video_id: str
    url: str
    thumbnail_id: str
    preference: int
    height: Optional[int] = None
    width: Optional[int] = None
    resolution: Optional[str] = None


@asset(
    io_manager_key="pydantic_io",
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def thumbnails(context: AssetExecutionContext, video_metadata: dict) -> list[Thumbnail]:
    """Extract and normalize metadata from raw youtube video metadata."""
    video_id = context.partition_key
    thumbnails = (
        [Thumbnail(video_id=video_id, thumbnail_id=t["id"], **t) for t in video_metadata["thumbnails"]]
        if "thumbnails" in video_metadata and video_metadata["thumbnails"] is not None
        else []
    )
    return thumbnails


class Heatmap(BaseModel):
    start_time: float
    end_time: float
    value: float


class Metadata(BaseModel):
    video_id: str
    title: str
    thumbnail: str
    description: str
    channel_id: str
    channel_url: str
    duration: int
    view_count: int
    age_limit: int
    webpage_url: str
    playable_in_embed: bool
    live_status: str
    channel: str
    channel_follower_count: int
    uploader: str
    uploader_id: str
    uploader_url: str
    upload_date: str
    availability: str
    original_url: str
    webpage_url_basename: str
    webpage_url_domain: str
    extractor: str
    extractor_key: str
    display_id: str
    fulltitle: str
    duration_string: str
    is_live: bool
    was_live: bool
    epoch: int
    format: str
    format_id: str
    ext: str
    protocol: str
    format_note: str
    tbr: float
    width: int
    height: int
    resolution: str
    fps: int
    dynamic_range: str
    vcodec: str
    aspect_ratio: float
    acodec: str
    asr: int
    audio_channels: int
    language: Optional[str]
    vbr: Optional[float]
    abr: Optional[float]
    comment_count: Optional[int]
    _format_sort_fields: list[str]
    requested_subtitles: Optional[bool]
    _has_drm: Optional[bool]
    playlist: Optional[bool]
    playlist_index: Optional[bool]
    license: Optional[str]
    heatmap: Optional[list[Heatmap]]
    release_timestamp: Optional[int]
    average_rating: Optional[bool]
    stretched_ratio: Optional[bool]
    release_date: Optional[str]
    filesize: Optional[int]
    source_preference: Optional[int]
    quality: Optional[float]
    has_drm: Optional[bool]
    url: Optional[str]
    language_preference: Optional[int]
    preference: Optional[str]
    video_ext: Optional[str]
    audio_ext: Optional[str]
    like_count: Optional[int]
    filesize_approx: Optional[int]


@asset(
    io_manager_key="pydantic_io",
    partitions_def=video_partition_def,
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def metadata(context: AssetExecutionContext, video_metadata: dict) -> Metadata:
    """Loads a Metadata table (dataframe) and remove columns corresponding to normalize tables."""
    video_id = context.partition_key
    ignore_cols = [
        "id",
        "thumbnails",
        "categories",
        "tags",
        "chapters",
        "subtitles",
        "formats",
        "automatic_captions",
        "requested_formats",
        "downloader_options",
        "http_headers",
    ]
    for col in ignore_cols:
        if col in video_metadata:
            del video_metadata[col]

    metadata = Metadata(video_id=video_id, **video_metadata)

    return metadata

from dagster import AssetExecutionContext, AutoMaterializePolicy, asset
from pytube import Stream, YouTube
from upath import UPath
from yt_dlp import YoutubeDL

from fastpipeline.assets.constants import BUCKET
from fastpipeline.partitions import video_partition_def


def fmt_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


@asset(
    partitions_def=video_partition_def,
    io_manager_key="json_io",
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def video_metadata(context: AssetExecutionContext) -> dict:
    """Metadata associated with fast.ai youtube videos."""
    video_id = context.partition_key
    video_url = fmt_youtube_url(video_id)
    context.log.info(f"Downloading metadata: {video_url}")
    with YoutubeDL({"quiet": True}) as ytdl:
        video_metadata = ytdl.extract_info(video_url, download=False)
    return video_metadata


def download_audio(video_id: str) -> tuple[bool, UPath]:
    """Downloads audio track given YouTube video_id"""
    path = BUCKET / f"{video_id}.mp4"
    url = fmt_youtube_url(video_id)

    existed = path.exists()
    if existed:
        # Find highest bit rate audio track for video
        video: Stream = (
            YouTube(url).streams.filter(only_audio=True, mime_type="audio/mp4").order_by("abr").last()
        )
        # Stream YouTube download to S3
        with path.open("wb") as file:
            video.stream_to_buffer(file)

    return existed, path


@asset(partitions_def=video_partition_def, auto_materialize_policy=AutoMaterializePolicy.eager())
def audio_files(context: AssetExecutionContext) -> UPath:
    """Audio tracks for fast.ai lectures."""
    video_id = context.partition_key
    existed, s3_uri = download_audio(video_id)
    # except AgeRestrictedError as err:
    #     context.log.error(f"AgeRestrictedError: {video_id}")
    if existed:
        context.log.info(f"CACHED: {video_id}")

    return s3_uri

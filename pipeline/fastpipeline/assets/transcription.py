import json
import os
from datetime import datetime

import httpx
import polars as pl
from dagster import AssetExecutionContext, AutoMaterializePolicy, asset
from upath import UPath

from fastpipeline.assets.constants import SEED_DIR
from fastpipeline.assets.metadata import Subtitle
from fastpipeline.partitions import video_partition_def
from fastpipeline.resources import ModalWhispher


def to_seconds(stamp: str) -> int:
    """Parse string VTT timestamp into number of seconds"""
    time = datetime.strptime(stamp, "%H:%M:%S.%f")
    seconds = int(time.hour * 60**2 + time.minute * 60 + time.second + time.microsecond / 1e6)
    return seconds


def parse_vtt(video_id: str, vtt_content: str) -> list[dict]:
    """Parse .vtt transcript from string."""
    blocks = vtt_content.split("\n\n")
    segments = []

    for idx, segment in enumerate(blocks[1:]):
        if len(segment) == 0:
            continue
        time_block, transcript = segment.split("\n", 1)
        start, end = time_block.split(" --> ")
        segments.append(
            {
                "video_id": video_id,
                "segment_id": idx,
                "start": to_seconds(start),
                "end": to_seconds(end),
                "text": transcript,
            }
        )
    return segments


@asset(partitions_def=video_partition_def)
def vtt_transcripts(context: AssetExecutionContext, subtitles: list[Subtitle]) -> dict[str, list[dict]]:
    """Student contributed fast.ai lecture transcripts."""
    transcripts = {}
    for subtitle in subtitles:
        if subtitle.ext != "vtt":
            continue
        context.log.info(f"Downloading {subtitle.language} VTT for {subtitle.video_id}")
        rsp = httpx.get(subtitle.url, timeout=10)
        rsp.raise_for_status()
        transcript = parse_vtt(subtitle.video_id, rsp.content.decode("utf8"))
        transcripts[subtitle.language] = transcript
    return transcripts


@asset(
    partitions_def=video_partition_def,
    io_manager_key="polars_io",
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def whispher_transcripts(
    context: AssetExecutionContext, audio_files: UPath, transcription_model: ModalWhispher
) -> pl.DataFrame:
    """OpenAI Whispher based fast.ai lecture transcripts."""
    video_id = context.partition_key

    cache_path = SEED_DIR / "transcripts" / audio_files.with_suffix(".json").name
    if cache_path.exists():
        context.log.info(f"CACHED VIDEO ID: {audio_files.stem}")
        with open(cache_path, "r") as file:
            transcript = json.load(file)
    else:
        context.log.info(f"UNCACHED VIDEO ID: {audio_files.stem}")
        transcript = transcription_model.transcribe(audio_files)
        # NOTE: Add transcript to cache to minimize cost. Shouldn't be used for true production.
        if os.getenv("DAGSTER_ENV", "local") == "prod":
            with cache_path.open("w") as file:
                json.dump(transcript, file)

    segment_df = pl.DataFrame(transcript["segments"]).with_columns(pl.lit(video_id).alias("video_id"))
    # transcript = {"video_id": s3_path.stem, "text": transcript["text"]}
    # transcripts_df = pl.DataFrame(transcripts)
    return segment_df


@asset(io_manager_key="polars_io", partitions_def=video_partition_def)
def raw_transcripts(
    vtt_transcripts: dict[str, list[dict]], whispher_transcripts: pl.DataFrame
) -> pl.DataFrame:
    """fast.ai lecture transcripts."""
    if "en" in vtt_transcripts:
        return pl.DataFrame(vtt_transcripts["en"]).with_columns(pl.lit("vtt").alias("kind"))
    else:
        return whispher_transcripts.with_columns(pl.lit("whispher").alias("kind"))


def merge_segments(segments: list[dict], video_id: str, segment_id: int) -> dict:
    starts = [segment["start"] for segment in segments]
    ends = [segment["end"] for segment in segments]
    return {
        "id": segment_id,
        "start": min(starts),
        "end": max(ends),
        "text": "".join([x["text"] for x in segments]),
        "video_id": video_id,
        "kind": segments[0]["kind"],
    }


@asset(
    partitions_def=video_partition_def,
    io_manager_key="polars_io",
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def processed_transcripts(context: AssetExecutionContext, raw_transcripts: pl.DataFrame) -> pl.DataFrame:
    """Merged fast.ai lecture transcripts."""
    video_id = context.partition_key
    segments = raw_transcripts.sort(by=pl.col("end")).to_dicts()
    if len(segments) <= 1:
        return raw_transcripts.select(["id", "start", "end", "text", "video_id", "kind"])

    max_duration = 30
    duration = 0
    merged = []
    buffer = []

    for segment in segments:
        # Merge buffer and add to array of merge segments. Reset duration and buffer array.
        if duration + segment["end"] - segment["start"] >= max_duration:
            merged.append(merge_segments(buffer, video_id, len(merged)))
            duration = 0
            buffer = []

        # Add segment to buffer and incriment run duration variable
        buffer.append(segment)
        duration += segment["end"] - segment["start"]

    df = pl.DataFrame(merged).rename({"id": "segment_id"})
    return df

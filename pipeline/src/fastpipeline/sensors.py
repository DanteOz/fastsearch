from dagster import (
    AssetSelection,
    DefaultSensorStatus,
    RunRequest,
    SensorEvaluationContext,
    SensorResult,
    SkipReason,
    sensor,
)
from yt_dlp import YoutubeDL

from fastpipeline.assets.scraping import audio_files, video_metadata
from fastpipeline.partitions import video_partition_def


def scrape_video_ids(seed_channels: list[str]) -> list[str]:
    """Scraped video ids for fast.ai lectures."""
    urls = []
    with YoutubeDL({"quiet": True}) as ytdl:
        for channel in seed_channels:
            info = ytdl.extract_info(url=channel, download=False, process=False)
            entries = list(info["entries"])
            if all(map(lambda e: "_type" in e and e["_type"] == "playlist", entries)):
                for playlist in entries:
                    urls.extend(map(lambda e: e["id"], playlist["entries"]))
            else:
                urls.extend(map(lambda e: e["id"], entries))
    return urls


@sensor(
    asset_selection=AssetSelection.keys(video_metadata.key, audio_files.key),
    minimum_interval_seconds=60 * 60 * 24,
    default_status=DefaultSensorStatus.RUNNING,
    description="Scrapes newly uploaded video ids and triggers pipeline runs.",
)
def videos_senor(context: SensorEvaluationContext):
    seed_channels = [
        "https://www.youtube.com/@howardjeremyp",
        "https://www.youtube.com/@rachelthomas4598",
    ]
    video_ids = scrape_video_ids(seed_channels)

    new_videos = []
    for video_id in video_ids:
        context.log.info(video_id)
        if not context.instance.has_dynamic_partition(video_partition_def.name, video_id):
            new_videos.append(video_id)

    if len(new_videos) == 0:
        return SkipReason("No new videos found.")

    return SensorResult(
        run_requests=[RunRequest(partition_key=video) for video in new_videos],
        dynamic_partitions_requests=[video_partition_def.build_add_request(new_videos)],
    )

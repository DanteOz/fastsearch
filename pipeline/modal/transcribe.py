import modal
from upath import UPath

stub = modal.Stub("fastsearch")

MODEL_NAME = "large"
CACHE_DIR = "/whisper"
CACHE_PATH = "/whisper/large-v2.pt"


def cache_model():
    """Cache OpenAI Whisper model in container."""
    import whisper

    whisper.load_model(MODEL_NAME, download_root=CACHE_DIR)


transcribe_image = (
    modal.Image.debian_slim()
    .apt_install("ffmpeg")
    .pip_install(["s3fs", "universal-pathlib", "openai-whisper", "torch"])
    .run_function(cache_model)
)


@stub.function(
    gpu="A10G",
    image=transcribe_image,
    secret=modal.Secret.from_name("fastsearch-aws"),
    concurrency_limit=10,
    timeout=7200,
)
def transcribe(path: UPath) -> dict:
    """Download audio file from AWS S3 using OpenAI Whispher."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    import torch
    import whisper

    logging.info(f"DOWNLOADING: {path}")

    path.fs.download(path.path, path.name)

    logging.info(f"LOADING: {CACHE_PATH}")
    model = whisper.load_model(CACHE_PATH).eval()
    logging.info(f"TRANSCRIBING: {CACHE_PATH}")
    with torch.inference_mode():
        transcript = model.transcribe(audio=path.name, fp16=True, language="en")

    logging.info(f"COMPLETED: {path}")
    return transcript

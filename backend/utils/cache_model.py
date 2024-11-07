import os
from transformers import AutoTokenizer
from huggingface_hub import login, hf_hub_download


def download_hub(repo_id: str):
    """Download model and tokenizer for model hub."""
    tokenizer = AutoTokenizer.from_pretrained(repo_id)
    model = hf_hub_download(repo_id, "model.onnx")


if __name__ == "__main__":
    login(token=os.getenv("HF_TOKEN"))
    download_hub(repo_id=os.getenv("RETRIEVER_MODEL"))
    download_hub(repo_id=os.getenv("RANKING_MODEL"))

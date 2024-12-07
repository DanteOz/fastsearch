import onnxruntime as ort
import transformers
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer

transformers.logging.set_verbosity_error()


class ONNXRetriever:
    def __init__(self, model_id: str) -> None:
        session_opts = ort.SessionOptions()
        session_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        model_path = hf_hub_download(model_id, "model.onnx", local_files_only=True)
        self.encoder = ort.InferenceSession(model_path, session_opts)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

    def __call__(self, query: str) -> list[float]:
        """Create embedding for user query."""
        tokens = self.tokenizer(query, return_tensors="np", truncation=True)
        embedding = self.encoder.run(None, dict(**tokens))
        return embedding[0].tolist()


class ONNXRanker:
    def __init__(self, model_id: str) -> None:
        session_opts = ort.SessionOptions()
        session_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        model_path = hf_hub_download(model_id, "model.onnx", local_files_only=True)
        self.ranker = ort.InferenceSession(model_path, session_opts)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

    def __call__(self, query: str, candidates: list[str], num_results: int) -> list[int]:
        """Reranks candidate documents against query. Returns list of ranked indicies."""
        tokens = self.tokenizer(
            [query for _ in range(len(candidates))],
            candidates,
            return_tensors="np",
            padding=True,
            truncation=True,
        )
        scores = self.ranker.run(None, dict(**tokens))
        return scores[0].argsort().tolist()[:num_results]

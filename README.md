# FastSearch

FastSearch is an end-to-end semantic search engine built to help tens of thousands of students search the popular fast.ai ~300-hour machine learning video corpus. Performs low-latency retrieval and ranking of lecture transcripts (_ONNX_), with bi- and cross-encoder models trained using cross-architecture knowledge distillation (_PyTorch_), on a custom dataset containing ~1,000 fast.ai questions and ~27,000 lecture segments. Backed by a data pipeline (_Dagster_) which scrapes and transcribes new video lectures (_OpenAl Whisper_) and incrementally updates an ANN search index (_Qdrant_). Tracks user queries and result feedback for model retraining. Deployed with fully custom CI/CD and MLOps (_GitHub Actions_) pipeline using IAC best practices (_AWS CDK_). MLOps pipeline launches backfill over the embedding/indexing pipeline and redeploys backend container with updated model weights upon push to model registry (_Hugging Face_).
<br></br>
<a href="http://fastsearch.danteoz.com">
<img src="https://github.com/DanteOz/fastsearch/blob/main/assets/btn-fastsearch.svg?sanitized=true"></a>
</a>
<br></br>
<a href="http://fastsearch.danteoz.com/writeup/scope.html">
<img src="https://github.com/DanteOz/fastsearch/blob/main/assets/btn-writeup.svg?sanitized=true"></a>
</a>
<br></br>
<a href="http://fastsearch.danteoz.com">
<img src="https://github.com/DanteOz/fastsearch/blob/main/frontend/public/writeup/img/fs-app.jpg?sanitized=true"></a>
</a>

> [!IMPORTANT]
> Since the write-up Fastsearch has migrated from Planetscale (MySQL) to Neon (Postgres).

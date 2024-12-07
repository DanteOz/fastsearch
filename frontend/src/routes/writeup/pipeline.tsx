import { WriteupTitle } from "~/components/writeup/Title";

export default function Pipeline() {
  return (
    <>
      <WriteupTitle>Data pipeline</WriteupTitle>
      <main>
        <article>
          <h1>Data Pipeline</h1>
          <p>
            At the core of FastSearch is a data pipeline composed of a
            <strong>scraping pipeline</strong> which
          </p>
          <ol>
            <li>downloads lecture recordings and metadata</li>
            <li>
              extracts and normalizes lecture metadata into a<span class="product">MySQL</span>{" "}
              database
            </li>
            <li>generates timestamped lecture transcripts (via GPU accelerated batch inference)</li>
          </ol>
          <img src="/img/writeup/data-scraping.png" alt="" />
          <p>
            Further, the <strong>indexing pipeline</strong>:
          </p>
          <ol start="4">
            <li>creates JSON payloads for the display and ranking of search results</li>
            <li>generates dense embeddings for lecture segments</li>
            <li>incrementally updates the ANN index with embeddings and search payloads</li>
            <li>rebuilds the ANN index when the embedding (bi-encoder) model changes</li>
          </ol>
          <img src="/img/writeup/data-indexing.png" alt="" />
          <h3>Transcripts</h3>
          <p>
            When available, FastSearch leverages <em>fast.ai</em> student contributed multilingual
            transcripts. This not only reduces transcription costs, but helps bootstrap next-version
            efforts to support multilingual search, by using English user feedback to pseudo-label
            machine translated queries and transcripts. For lectures missing English transcripts,
            FastSearch falls back on
            <span class="product">OpenAI Whisper</span> to generate high quality machine
            transcriptions.
          </p>
          <p>
            Lecture transcripts are partitioned by language and stored in a versioned{" "}
            <span class="product">AWS S3</span> bucket, where they are queried using{" "}
            <span class="product">DuckDB</span> (with full text search extension) during model
            development. This allows for efficient querying of the transcript corpus by metadata or
            text, without needing a development instance of ElasticSearch or MongoDB.
          </p>
          <blockquote>
            <p class="bq-title">Coming in FastSearch 2.0</p>
            <p>
              Once enough user feedback is collected, multilingual transcripts will be used to
              bootstrap support for other languages by this process flow:
            </p>
          </blockquote>
          <img src="/img/writeup/transcripts.png" alt="" />
          <h3>Metadata</h3>
          <p>
            Each lecture FastSearch scrapes from YouTube contains 69 metadata fields. Eighteen of
            the fields are extracted into third norm form and stored in a{" "}
            <span class="product">MySQL</span> database. This ensures data quality for downstream
            analysis and model development order by enforcing a strict relational data model.
          </p>
          <p>
            There are three categories of stored metadata: <em>YouTube</em> (id, channel_id, upload
            date…), <em>video</em> (title, description, duration…) and <em>content</em> (chapters,
            categories, tags…). Content metadata is used during data labeling for topic-aware
            sampling for candidate search results. YouTube and video metadata are joined with
            references to <em>fast.ai</em> course materials to form the JSON search payloads stored
            in <span class="product">Qdrant</span> vector DB.
          </p>
          <img src="/img/writeup/erd.png" alt="" class="borderless" />
          <img src="/img/writeup/payload.png" alt="" />

          <div class="prevnext">
            <a href="/writeup/training">Model training</a>
            <a href="/writeup/backend">Backend</a>
          </div>
        </article>
      </main>
    </>
  );
}

import { WriteupTitle } from "~/components/writeup/Title";

export default function Semantic() {
  return (
    <>
      <WriteupTitle>Semantic search</WriteupTitle>
      <main>
        <article>
          <h1>Semantic search</h1>
          <p>
            In order to support the problematic case where
            <em>fast.ai</em> students might not know exactly what they're looking for or might not
            use domain specific keywords, FastSearch implements a semantic search algorithm. A more
            common approach would have been a lexical search engine, like ElasticSearch, with a
            predictable process flow like this:
          </p>
          <img src="/writeup/img/lexical.png" alt="" />
          <p>
            While lexical search works by decomposing queries into tokens, retrieving documents from
            an inverted index, and ranking candidates using sparse BM25 vectors and cosine
            similarity, they struggle to represent meaning using only keywords. For example, a user
            searching textbook titles for “data processing in python” won’t find a textbook entitled{" "}
            <em>Introduction to Pandas</em>, even though "pandas" is very relevant to the query.
          </p>

          <p>
            FastSearch addresses this limitation by using neural networks to learn dense vector
            representations in an embeddings space where vectors with similar meanings are closer
            together. Transformers are well suited to learn this embedding space as their
            self-attention layers directly learn the interactions between tokens in text.
          </p>
          <img src="/writeup/img/semantic.png" alt="" />

          <div class="prevnext">
            <a href="/writeup/scope">Application scope</a>
            <a href="/writeup/training">Model training</a>
          </div>
        </article>
      </main>
    </>
  );
}

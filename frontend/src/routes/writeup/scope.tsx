import { WriteupTitle } from "~/components/writeup/Title";

export default function Scope() {
  return (
    <>
      <WriteupTitle>Scope</WriteupTitle>
      <main>
        <article>
          <h1>Application scope</h1>
          <p>
            <em>fast.ai</em> is one of the best resources for machine learning. Over the last six
            years they have released 238 videos spanning 291 hours of free lectures, as well as a
            book, Github repos, a deep learning library, documentation, notebooks, and so on.
          </p>
          <h3>Problem space</h3>
          <p>
            Meanwhile, the scope of machine learning has progressed exponentially over that
            timeline, so not every topic is covered in each course (for example, object detection
            was last covered in 2019). This causes students to often ask questions on the{" "}
            <em>fast.ai</em> forums about topics which have been covered in previous years but are
            not present in the most recent iteration of the course. Furthermore, while video
            lectures are at the core of the <em>fast.ai</em> knowledge base, at 2-3 hours per
            lecture, they aren't easily searchable due to their length and visual modality.
          </p>
          <h3>Solution</h3>
          <p>
            Fortunately, course lectures convey information primarily via speech, speech can be
            captured in transcripts, and timestamped transcripts can be treated as a document corpus
            over which well understood information retrieval methods can be applied.
          </p>
          <p>
            I thus built FastSearch, a semantic search engine and indexing pipeline which utilize
            all six years of <em>fast.ai</em>
            lectures to find exact timestamps relevant to thousands of student questions:
          </p>
          <img src="/writeup/img/fs-app.jpg" alt="" class="borderless" style="border-radius: 8px" />
          <div class="prevnext first">
            <a href="/writeup/semantic">Semantic search</a>
          </div>
        </article>
      </main>
    </>
  );
}

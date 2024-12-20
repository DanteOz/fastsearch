import { WriteupTitle } from "~/components/writeup/Title";

export default function Feedback() {
  return (
    <>
      <WriteupTitle>Feedback loop</WriteupTitle>
      <main>
        <article>
          <h1>Feedback loop</h1>
          <p>
            In order to continuously improve the relevancy of results, FastSearch tracks all user
            queries and search result ratings.
            <em>Search result ratings</em> are strong signals of user preference and can be directly
            trained on to improve both cross-encoder (ranking) and bi-encoder (retrieval) models.{" "}
            <em>User queries</em> improve the domain coverage of the query corpus and can be used
            generate more diverse query+result candidates for data labeling.
          </p>
          <h3>Feedback UI</h3>
          <img
            src="/img/writeup/feedback-ui.jpg"
            alt=""
            class="borderless"
            style="border-radius: 8px"
          />
          <p>
            FastSearch was designed as a Single Page App (SPA) to increase the likelihood of users
            providing feedback by eliminating all navigation across multiple pages, making it easy
            for users to scan results and activate videos <em>in place</em>, and placing the
            feedback component right next to the video player.
          </p>
          <p>
            Clicking on an item In the result list opens an embedded YouTube player queued to its
            exact timestamp <span class="point">1</span>. Directly underneath the player are
            feedback components
            <span class="point">2</span> and links to related course materials
            <span class="point">3</span>. This reduces the chance that a user finds a relevant
            search result, views it in another page, and never comes back to rate it.
          </p>
          <h3>Storing Feedback</h3>
          <p>
            All user feedback is written to a MySQL database. User queries are stored
            asynchronously, via background tasks scheduled on the FastAPI framework event loop, in
            order to reduce the latency created by database connection and transaction.
          </p>
          <img src="/img/writeup/feedback-sync.png" alt="" />
          <img src="/img/writeup/feedback-async.png" alt="" />
          <blockquote>
            <p class="bq-title">Coming in FastSearch 2.0</p>
            <p>
              The resiliency of feedback storage will be improved by switching to an asynchronous
              queue such as <strong>AWS SQS</strong> or
              <strong>Kafka</strong>.
            </p>
            <p>
              Also, as usage of FastSearch grows, clickstream data – including
              results-clicked-per-query, result watch time, result-query abandonment – will be
              tracked. These events will be used as weak signals to fill in the gaps when users
              don’t provide explicit feedback. For example, a search result with a long watch-time
              and high cross-encoder score likely indicates a relevant search result, especially if
              the user closed the page after. This can be modeled using clickstream events as
              features to improve the ranking model used to generate pseudo labels during training.
            </p>
          </blockquote>
          <div class="prevnext">
            <a href="/writeup/backend">Backend</a>
            <a href="/writeup/deployment">Deployment & MLOps</a>
          </div>
        </article>
      </main>
    </>
  );
}

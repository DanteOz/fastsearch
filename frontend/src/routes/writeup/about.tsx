import { WriteupTitle } from "~/components/writeup/Title";

export default function About() {
  return (
    <>
      <WriteupTitle>About & Links</WriteupTitle>
      <main>
        <article>
          <h1>Links</h1>
          <p>
            I am <strong>Dante Secada-Oz</strong>, a graduate of Rochester Institute of Technology
            (RIT) in Software Engineering, with experience in building and deploying data/machine
            learning driven applications using real world data.
          </p>
          <p>
            I am looking for a full-time position as a <strong>Machine Learning Engineer</strong> in
            NLP, information retrieval, recommender systems and LLMs on domain specific corpora.
          </p>

          <div class="btns">
            <div class="btn search">
              <a href="/" target="_blank" />
              <div>Website</div>
            </div>

            <div class="btn repo">
              <a href="https://github.com/DanteOz/fastsearch" target="_blank" />
              <div>Repo</div>
            </div>

            <div class="btn resume">
              <a href="https://danteoz.com/resume.pdf" target="_blank" />
              <div>Bio</div>
            </div>

            <div class="btn email">
              <a href="mailto:contact@danteoz.com" target="_blank" />
              <div>Contact</div>
            </div>

            <div class="btn linkedin">
              <a href="https://www.linkedin.com/in/danteoz" target="_blank" />
              <div>Connect</div>
            </div>

            <div class="btn twitter">
              <a href="https://twitter.com/DanteOzML" target="_blank" />
              <div>Follow</div>
            </div>
          </div>

          <div class="prevnext last">
            <a href="/writeup/deployment">Deployment & MLOps</a>
          </div>
        </article>
      </main>
    </>
  );
}

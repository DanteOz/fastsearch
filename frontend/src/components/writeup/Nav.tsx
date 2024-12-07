import { A } from "@solidjs/router";

export function WriteupNav() {
  return (
    <nav>
      <div class="logo" />
      <A href="/writeup/scope" activeClass="selected">
        Application scope
      </A>
      <A href="/writeup/semantic" activeClass="selected">
        Semantic search
      </A>
      <A href="/writeup/training" activeClass="selected">
        Model training
      </A>
      <A href="/writeup/pipeline" activeClass="selected">
        Data pipeline
      </A>
      <A href="/writeup/backend" activeClass="selected">
        Backend
      </A>
      <A href="/writeup/feedback" activeClass="selected">
        Feedback loop
      </A>
      <A href="/writeup/deployment" activeClass="selected">
        Deployment & MLOps
      </A>
      <A href="/writeup/about" class="nav-below" activeClass="selected">
        About & Links
      </A>
    </nav>
  );
}

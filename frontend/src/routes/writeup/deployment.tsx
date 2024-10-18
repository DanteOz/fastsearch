import { WriteupTitle } from "~/components/writeup/Title";

export default function Deployment() {
  return (
    <>
      <WriteupTitle>Deployment & MLOps</WriteupTitle>
      <main>
        <article>
          <h1>Deployment & MLOps</h1>
          <p>
            FastSearch is deployed on a serverless architecture in order to minimize hosting costs
            while enabling horizontal scaling. The frontend is served from an{" "}
            <span class="product">AWS S3</span> bucket and uses
            <span class="product">AWS CloudFront</span> as a CDN in order to cache static files,
            terminate SSL handshakes closer to the user and reverse proxy the backend API. The
            backend is hosted as a containerized
            <span class="product">AWS App Runner</span> endpoint.
          </p>
          <img src="/img/writeup/deployment.png" alt="" />

          <h3>CI/CD pipeline</h3>
          <p>
            FastSearch uses <span class="product">AWS CDK</span> as its infrastructure-as-code
            framework for declarative configuration and deployment. This enables FastSearch to
            version infrastructure alongside source code and leverage prebuilt best practices such
            as CDN cache invalidation on frontend deployments.
            <span class="product">Github Actions</span> are used to build the frontend static files
            and backend docker container, and also deploy any changes to the infrastructure when a
            feature branch is merged into main on the FastSearch GitHub repo.
          </p>

          <h3>Model Redeployment</h3>
          <p>
            FastSearch leverages
            <span class="product">Hugging Face Model Hub</span> webhooks and
            <span class="product">Github Actions</span> to rebuild and deploy the backend Docker
            image whenever the cross-encoder or bi-encoder model weights are updated. Whenever the
            bi-encoder model is updated, an additional batch of inference jobs in the FastSearch
            data pipeline is triggered in order to rebuild the ANN index of all lecture transcripts.
          </p>

          <img src="/img/writeup/mlops.png" alt="" class="bkz" />

          <div class="prevnext">
            <a href="/writeup/feedback">Feedback loop</a>
            <a href="/writeup/about">About & Links</a>
          </div>
        </article>
      </main>
    </>
  );
}

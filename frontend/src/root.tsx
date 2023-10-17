// @refresh reload
import { Suspense } from "solid-js";
import {
  A,
  Body,
  ErrorBoundary,
  FileRoutes,
  Head,
  Html,
  Meta,
  Routes,
  Scripts,
  Title,
} from "solid-start";
import "./root.css";

export default function Root() {
  return (
    <Html lang="en">
      <Head>
        <Title>FastSearch</Title>
        <Meta charset="utf-8" />
        <Meta name="viewport" content="width=device-width, initial-scale=1" />

        {/* Primary Meta Tags */}
        <Meta name="title" content="FastSearch" />
        <Meta
          name="description"
          content="Semantic search for fast.ai lectures."
        />
        {/* Open Graph / Facebook */}
        <Meta property="og:type" content="website" />
        <Meta property="og:url" content="https://fastsearch.danteoz.com/" />
        <Meta property="og:title" content="FastSearch" />
        <Meta
          property="og:description"
          content="Semantic search for fast.ai lectures."
        />
        <Meta property="og:locale" content="en_US" />
        {/* Twitter */}
        <Meta property="twitter:card" content="summary_large_image" />
        <Meta
          property="twitter:url"
          content="https://fastsearch.danteoz.com/"
        />
        <Meta property="twitter:title" content="FastSearch" />
        <Meta
          property="twitter:description"
          content="Semantic search for fast.ai lectures."
        />

        <script
          defer
          src="https://static.cloudflareinsights.com/beacon.min.js"
          data-cf-beacon='{"token": "9f445c7464784e0e851ca0fc7ff0a4f9"}'
        ></script>
      </Head>
      <Body>
        <Suspense>
          <ErrorBoundary>
            <Routes>
              <FileRoutes />
            </Routes>
          </ErrorBoundary>
        </Suspense>
        <Scripts />
      </Body>
    </Html>
  );
}

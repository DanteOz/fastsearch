import { MetaProvider, Meta, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";
import { Suspense } from "solid-js";

export default function App() {
  return (
    <Router
      root={(props) => (
        <MetaProvider>
          <Title>FastSearch</Title>
          <Meta charset="utf-8" />
          <Meta name="viewport" content="width=device-width, initial-scale=1" />
          {/* Primary Meta Tags */}
          <Meta name="title" content="FastSearch" />
          <Meta name="description" content="Semantic search for fast.ai lectures." />
          {/* Open Graph / Facebook */}
          <Meta property="og:type" content="website" />
          <Meta property="og:url" content="https://fastsearch.danteoz.com/" />
          <Meta property="og:title" content="FastSearch" />
          <Meta property="og:description" content="Semantic search for fast.ai lectures." />
          <Meta property="og:locale" content="en_US" />
          {/* Twitter */}
          <Meta property="twitter:card" content="summary_large_image" />
          <Meta property="twitter:url" content="https://fastsearch.danteoz.com/" />
          <Meta property="twitter:title" content="FastSearch" />
          <Meta property="twitter:description" content="Semantic search for fast.ai lectures." />
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}

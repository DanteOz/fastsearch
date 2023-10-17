import { ErrorBoundary, Suspense } from "solid-js";
import SearchBar from "~/components/Search.jsx";
import Results from "~/components/Results.jsx";
import Theater from "~/components/Theater.jsx";
import NavBar from "~/components/Navbar";
import { SearchContextProvider } from "~/lib/Context";

const ErrorMessage = (error: Error) => {
  return (
    <div id="warningPanel">
      <img src="/img/warning.svg" alt="warning" />
      {error.message}
      <span>, please search again.</span>
    </div>
  );
};

export default function App() {
  return (
    <SearchContextProvider>
      <main>
        <div id="header">
          <NavBar />
          <SearchBar />
        </div>
        <ErrorBoundary fallback={(error) => <ErrorMessage error={error} />}>
          <div id="content" class="content">
            <Suspense>
              <Theater />
              <Results />
            </Suspense>
          </div>
        </ErrorBoundary>
      </main>
    </SearchContextProvider>
  );
}

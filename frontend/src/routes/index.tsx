import {
  ErrorBoundary,
  Suspense,
  For,
  onCleanup,
  onMount,
  startTransition,
  createSignal,
  Show,
  untrack,
  createMemo,
  createEffect,
} from "solid-js";
import { useSearchContext, SearchContextProvider, Feedback } from "~/lib/Context";

import "~/components/Navbar.css";
import "~/components/Results.css";
import "~/components/Search.css";
import "~/components/Theater.css";

// Helper
function secToHMS(sec: number): string {
  return new Date(sec * 1000).toISOString().slice(11, 19);
}

// Fetch
async function submitFeedback(props: { feedback: number; query: string; result_id: string }) {
  return await fetch("/api/feedback", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(props),
  }).then((response) => {
    if (!response.ok) {
      throw new Error(`${response.status} | ${response.statusText}`);
    }
  });
}

// Components
function ErrorMessage(props: { error: Error }) {
  return (
    <div id="warningPanel">
      <img src="/img/warning.svg" alt="warning" />
      {props.error.message}
      <span>, please search again.</span>
    </div>
  );
}

function NavBar() {
  return (
    <div class="tabsPanel">
      <img src="/img/logo.svg" alt="FastSearch logo" />
      <div class="tabs">
        <a href="/writeup/scope.html">PROJECT WRITEUP</a>
      </div>
    </div>
  );
}

function SearchBar() {
  let searchBox: HTMLInputElement | undefined;
  let placeholder = "Search fast.ai videos & resources...";

  const { setQuery } = useSearchContext();

  const handleQuery = (event: KeyboardEvent | MouseEvent) => {
    if (searchBox) {
      if (event instanceof KeyboardEvent && event.key !== "Enter") {
        return;
      }

      let rawQuery = searchBox.value.trim();
      if (rawQuery.length > 0) {
        startTransition(() => setQuery(rawQuery));
        searchBox.classList.remove("alerto");
      } else {
        if (event instanceof KeyboardEvent) {
          alert("Please enter search term(s)...");
        } else if (event instanceof MouseEvent) {
          searchBox.placeholder = "Please enter search term(s)...";
          searchBox.classList.add("alerto");
        }
      }
    }
  };

  onMount(() => document.addEventListener("keypress", handleQuery));
  onCleanup(() => document.removeEventListener("keypress", handleQuery));

  return (
    <div class="searchPanel">
      <input
        type="text"
        id="search"
        ref={searchBox}
        name="search"
        placeholder={placeholder}
        onFocus={() => (searchBox!.placeholder = "")}
        onBlur={() => (searchBox!.placeholder = placeholder)}
        required
      />
      <button id="btn-clear" onClick={() => (searchBox!.value = "")}></button>
      <button id="btn-search" onClick={handleQuery}></button>
    </div>
  );
}

function Results() {
  const { results, selected, setSelected } = useSearchContext();

  const handleSelection = (index: number) => {
    window.scrollTo(0, 0);
    setSelected(index);
  };

  return (
    <ul id="results">
      <For each={results()}>
        {(result, i) => (
          <li onClick={[handleSelection, i]} classList={{ selected: selected() === i() }}>
            <div class="meta">
              <div class="vid">{result.title}</div>
              <div class="seg">
                <div>
                  <span>{secToHMS(result.start)}</span>
                  {result.text}
                </div>
              </div>
            </div>
            <img src={result.thumbnail} alt={`Thumbnail for ${result.title}.`} />
          </li>
        )}
      </For>
    </ul>
  );
}

function Theater() {
  const { query, results, selected, feedback, setFeedback } = useSearchContext();
  const result = createMemo(() => {
    return selected() || selected() == 0 ? results()[selected()!] : null;
  });
  const handleFeedback = (fb: Feedback) => {
    if (fb && fb !== feedback[selected()!]) {
      try {
        submitFeedback({
          feedback: fb,
          query: untrack(query)!,
          result_id: result()!.video_id,
        });
        setFeedback(selected()!, fb);
      } catch (e) {
        alert("Failed to submit feedback. Please retry.");
      }
    }
  };
  const [restart, setRestart] = createSignal(false, { equals: false });
  createEffect(() => {
    // When selected result changes, reset autoplay
    selected();
    setRestart(false);
  });

  const url = () =>
    `https://www.youtube-nocookie.com/embed/${result()!.video_id}?start=${
      result()!.start
    }&autoplay=${restart() ? 1 : 0}&rel=0`;

  return (
    <div class="theater" classList={{ slideDown: result() }}>
      <Show when={result()}>
        <div id="videoPanel">
          <iframe
            id="player"
            width="720"
            height="405"
            src={url()}
            title="YouTube video player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
        <div id="metaPanel" class="metaPanel">
          <div class="top">
            <div>
              <button id="segmentStart" onClick={[setRestart, true]}>
                {secToHMS(result()!.start)}
              </button>
              Restart segment
            </div>

            <div id="feedback">
              <div>Rate this result</div>
              <button
                id="btn-fb-yes"
                onClick={[handleFeedback, 1]}
                classList={{ selectedYES: feedback[selected()!] === 1 }}
              ></button>
              <button
                id="btn-fb-no"
                onClick={[handleFeedback, -1]}
                classList={{ selectedNO: feedback[selected()!] === -1 }}
              ></button>
            </div>
          </div>

          <div id="resources">
            <div>fast.ai</div>
            <a
              id="lesson"
              href={result()!.lesson || ""}
              target="_blank"
              classList={{ "btn-disabled": !result()!.lesson }}
            >
              Lesson
            </a>
            <a
              id="forum"
              href={result()!.forum || ""}
              target="_blank"
              classList={{ "btn-disabled": !result()!.forum }}
            >
              Forum
            </a>
            <a
              id="course"
              href={result()!.course || ""}
              target="_blank"
              classList={{ "btn-disabled": !result()!.course }}
            >
              Course
            </a>
          </div>
        </div>
      </Show>
    </div>
  );
}

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

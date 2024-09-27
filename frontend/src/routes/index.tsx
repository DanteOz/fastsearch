import {
  ErrorBoundary,
  Suspense,
  For,
  startTransition,
  createSignal,
  Show,
  untrack,
  createMemo,
  createEffect,
  createResource,
  type Accessor,
  type Setter,
} from "solid-js";
import { type SetStoreFunction, createStore } from "solid-js/store";
import * as v from "valibot";

import "~/components/Navbar.css";
import "~/components/Results.css";
import "~/components/Search.css";
import "~/components/Theater.css";

// Helper
function secToHMS(sec: number): string {
  return new Date(sec * 1000).toISOString().slice(11, 19);
}

function initFeedback(n: number) {
  return Array(n).fill(null);
}

// Types

const ResultsSchema = v.array(
  v.object({
    id: v.number(),
    video_id: v.string(),
    title: v.string(),
    text: v.string(),
    start: v.number(),
    thumbnail: v.string(),
    lesson: v.nullable(v.string()),
    forum: v.nullable(v.string()),
    course: v.nullable(v.string()),
  })
);

const SearchFormSchema = v.object({
  query: v.pipe(v.string(), v.trim(), v.minLength(1, "Please enter search term(s)...")),
});

type Results = v.InferOutput<typeof ResultsSchema>;
type Feedback = -1 | null | 1;

// Data Fetching

async function fetchResults(query: string) {
  const params = new URLSearchParams({ query: query });
  const resp = await fetch(`/api/search?${params.toString()}`, {
    headers: { "Content-Type": "application/json" },
  });
  if (!resp.ok) {
    throw new Error(`${resp.status} | ${resp.statusText}`);
  }
  const data = await resp.json();
  const results = v.parse(ResultsSchema, data);
  return results;
}

async function submitFeedback(props: { feedback: number; query: string; result_id: string }) {
  const response = await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(props),
  });

  if (!response.ok) {
    throw new Error(`${response.status} | ${response.statusText}`);
  }
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

function SearchBar(props: { setQuery: Setter<string | null> }) {
  const submitSearch = (event: SubmitEvent) => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement | null;
    if (form) {
      const data = v.safeParse(SearchFormSchema, Object.fromEntries(new FormData(form)));
      if (data.success) {
        startTransition(() => props.setQuery(data.output.query));
      } else {
        alert(data.issues[0].message);
      }
    }
  };

  return (
    <search>
      <form name="search" onsubmit={submitSearch}>
        <input
          type="text"
          id="query"
          name="query"
          placeholder={"Search fast.ai videos & resources..."}
        />
        <button id="btn-clear" type="reset" />
        <button id="btn-search" type="submit" />
      </form>
    </search>
  );
}

function Result(props: {
  result: Results[number];
  index: Accessor<number>;
  selected: Accessor<number | null>;
  setSelected: Setter<number | null>;
}) {
  const handleSelection = (index: number) => {
    window.scrollTo(0, 0);
    props.setSelected(index);
  };

  return (
    <li
      onClick={[handleSelection, props.index]}
      classList={{ selected: props.selected() === props.index() }}
    >
      <div class="meta">
        <div class="vid">{props.result.title}</div>
        <div class="seg">
          <div>
            <span>{secToHMS(props.result.start)}</span>
            {props.result.text}
          </div>
        </div>
      </div>
      <img src={props.result.thumbnail} alt={`Thumbnail for ${props.result.title}.`} />
    </li>
  );
}

function Theater(props: {
  results: Accessor<Results>;
  query: Accessor<string | null>;
  selected: Accessor<number | null>;
  feedback: Feedback[];
  setFeedback: SetStoreFunction<Feedback[]>;
}) {
  const [restart, setRestart] = createSignal(false, { equals: false });
  const result = createMemo(() => {
    return props.selected() || props.selected() === 0 ? props.results()[props.selected()!] : null;
  });
  const handleFeedback = (fb: Feedback) => {
    // check that the feedback signal has not updated in value
    // TRY: to submit the feedback
    // CATCH: response error
    if (fb && fb !== props.feedback[props.selected()!]) {
      try {
        submitFeedback({
          feedback: fb,
          query: untrack(props.query)!,
          result_id: result()!.video_id,
        });
        props.setFeedback(props.selected()!, fb);
      } catch (e) {
        alert("Failed to submit feedback. Please retry.");
      }
    }
  };

  createEffect(() => {
    // When selected result changes, reset autoplay
    props.selected();
    setRestart(false);
  });

  const url = () =>
    `https://www.youtube-nocookie.com/embed/${result()!.video_id}?start=${
      result()!.start
    }&autoplay=${restart() ? 1 : 0}&rel=0`;

  return (
    <div class="theater" classList={{ slideDown: !!result() }}>
      <Show when={result()}>
        <div id="videoPanel">
          <iframe
            id="player"
            width="720"
            height="405"
            src={url()}
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          />
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
                classList={{ selectedYES: props.feedback[props.selected()!] === 1 }}
              />
              <button
                id="btn-fb-no"
                onClick={[handleFeedback, -1]}
                classList={{ selectedNO: props.feedback[props.selected()!] === -1 }}
              />
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
              rel="noreferrer"
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
  const [query, setQuery] = createSignal<string | null>(null);
  const [results] = createResource(query, fetchResults, { initialValue: [] });
  const [feedback, setFeedback] = createStore<Feedback[]>([]);
  const [selected, setSelected] = createSignal<number | null>(null);

  // TODO: Refactor to push selected in results data structure
  createEffect(() => {
    setFeedback(initFeedback(results().length));
    setSelected(null);
  });

  return (
    <main>
      <div id="header">
        <div class="tabsPanel">
          <img src="/img/logo.svg" alt="FastSearch logo" />
          <div class="tabs">
            <a href="/writeup/scope.html">PROJECT WRITEUP</a>
          </div>
        </div>
        <SearchBar setQuery={setQuery} />
      </div>
      <div id="content" class="content">
        <ErrorBoundary fallback={(error) => <ErrorMessage error={error} />}>
          <Suspense>
            <Theater
              results={results}
              query={query}
              selected={selected}
              feedback={feedback}
              setFeedback={setFeedback}
            />
            <ul id="results">
              <For each={results()}>
                {(result, index) => (
                  <Result
                    result={result}
                    index={index}
                    selected={selected}
                    setSelected={setSelected}
                  />
                )}
              </For>
            </ul>
          </Suspense>
        </ErrorBoundary>
      </div>
    </main>
  );
}

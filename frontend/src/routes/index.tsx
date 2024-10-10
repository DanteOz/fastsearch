import {
  action,
  cache,
  createAsync,
  type AccessorWithLatest,
  type RouteDefinition,
  useSearchParams,
} from "@solidjs/router";
import {
  ErrorBoundary,
  Suspense,
  For,
  startTransition,
  createSignal,
  Show,
  createMemo,
  createEffect,
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
const getResults = cache(async (query: string | undefined) => {
  if (!query || query === "") return [] as Results;
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
}, "results");

const submitFeedback = action(
  async (props: { feedback: number; query: string; result_id: string }) => {
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(props),
    });

    if (!response.ok) {
      throw new Error(`${response.status} | ${response.statusText}`);
    }
  },
  "feedback"
);

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

function SearchBar() {
  const [searchParams, setSearchParams] = useSearchParams();
  const submitSearch = (event: SubmitEvent) => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement | null;
    if (form) {
      const data = v.safeParse(SearchFormSchema, Object.fromEntries(new FormData(form)));
      if (data.success) {
        startTransition(() => setSearchParams({ q: data.output.query }));
      } else {
        alert(data.issues[0].message);
      }
    }
  };

  return (
    <search>
      <form name="search" onsubmit={submitSearch}>
        <input
          type="search"
          id="query"
          name="query"
          value={searchParams.q ?? ""}
          placeholder="Search fast.ai videos & resources..."
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

function FeedbackForm() {
  return (
    <form name="feedback">
      <input type="hidden" name="result_id" value={""} />
      <input type="hidden" name="query" value={""} />
      <input type="hidden" name="feedback" value={""} />
    </form>
  );
}

function Theater(props: {
  results: AccessorWithLatest<Results>;
  selected: Accessor<number | null>;
  feedback: Feedback[];
  setFeedback: SetStoreFunction<Feedback[]>;
}) {
  const [searchParams] = useSearchParams();
  let player!: HTMLIFrameElement;
  const url = () => {
    return `https://www.youtube-nocookie.com/embed/${result()!.video_id}?start=${
      result()!.start
    }&autoplay=1&rel=0`;
  };

  const result = createMemo(() => {
    return props.selected() || props.selected() === 0 ? props.results()[props.selected()!] : null;
  });

  const handleFeedback = (feedback: Feedback) => {
    // check that the feedback signal has not updated in value
    // TRY: to submit the feedback
    // CATCH: response error
    if (feedback && feedback !== props.feedback[props.selected()!]) {
      try {
        submitFeedback({
          feedback: feedback,
          query: searchParams.q!,
          result_id: result()!.video_id,
        });
        props.setFeedback(props.selected()!, feedback);
      } catch (e) {
        alert("Failed to submit feedback. Please retry.");
      }
    }
  };

  return (
    <div class="theater" classList={{ slideDown: !!result() }}>
      <Show when={result()}>
        <div id="videoPanel">
          <iframe
            id="player"
            ref={player}
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
              <button
                id="segmentStart"
                type="button"
                onclick={() => player.setAttribute("src", url())}
              >
                {secToHMS(result()!.start)}
              </button>
              Restart segment
            </div>

            <div id="feedback">
              <div>Rate this result</div>
              <button
                id="btn-fb-yes"
                type="button"
                onClick={[handleFeedback, 1]}
                classList={{
                  selectedYES: props.feedback[props.selected()!] === 1,
                }}
              />
              <button
                id="btn-fb-no"
                type="button"
                onClick={[handleFeedback, -1]}
                classList={{
                  selectedNO: props.feedback[props.selected()!] === -1,
                }}
              />
            </div>
          </div>

          <div id="resources">
            <div>fast.ai</div>
            <a
              id="lesson"
              href={result()!.lesson || ""}
              target="_blank"
              rel="noreferrer"
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
              rel="noreferrer"
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

export const route = {
  preload(props) {
    getResults(props.params.q);
  },
} satisfies RouteDefinition;

export default function App() {
  const [searchParams] = useSearchParams();
  const results = createAsync(() => getResults(searchParams.q), { initialValue: [] });
  const [feedback, setFeedback] = createStore<Feedback[]>([]);
  const [selected, setSelected] = createSignal<number | null>(null);

  // TODO: Refactor to push selected in results data structure
  createEffect(() => {
    setFeedback(initFeedback(results()!.length));
    setSelected(null);
  });

  return (
    <main>
      <header>
        <div class="tabsPanel">
          <img src="/img/logo.svg" alt="FastSearch logo" />
          <div class="tabs">
            <a href="/writeup/scope.html">PROJECT WRITEUP</a>
          </div>
        </div>
        <SearchBar />
      </header>
      <div id="content" class="content">
        <ErrorBoundary fallback={(error) => <ErrorMessage error={error} />}>
          <Suspense>
            <Theater
              results={results}
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

/**
 * TODO:
 *
 * - Try using html form get action for search submission
 * -
 *
 */

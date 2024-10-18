import {
  action,
  cache,
  useSearchParams,
  type AccessorWithLatest,
  type RouteDefinition,
  createAsyncStore,
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
  untrack,
} from "solid-js";
import { type SetStoreFunction, createStore } from "solid-js/store";
import * as v from "valibot";

import "~/styles/app.css";
import "~/styles/Navbar.css";
import "~/styles/Results.css";
import "~/styles/Search.css";
import "~/styles/Theater.css";

// Helper
function secToHMS(sec: number): string {
  return new Date(sec * 1000).toISOString().slice(11, 19);
}

function createFeedbackArray(num: number) {
  return Array(num).fill(null) as Feedback[];
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
type Feedback = -1 | 1;

// Data Fetching
const getResults = cache(async (query: string) => {
  const params = new URLSearchParams({ query: query });
  const resp = await fetch(`/api/search?${params.toString()}`, {
    headers: { "Content-Type": "application/json" },
  });
  if (!resp.ok) {
    throw new Error(`search request failed (http: ${resp.status})`);
  }
  const data = await resp.json();
  const results = v.parse(ResultsSchema, data);
  return results;
}, "results");

const postFeedback = action(
  async (props: { feedback: Feedback; query: string; result_id: string }) => {
    console.log("posting");
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(props),
    });

    if (!response.ok) {
      throw new Error(`could not submit feedback (${response.status})`);
    }
    return true;
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

function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const submitSearch = (event: SubmitEvent) => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
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
          type="text"
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
    // biome-ignore lint/a11y/useKeyWithClickEvents:
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

// Show feedback

// INVARIANT: selected should always be true
function Theater(props: {
  results: AccessorWithLatest<Results>;
  selected: Accessor<number | null>;
  feedback: Feedback[];
  setFeedback: SetStoreFunction<Feedback[]>;
}) {
  const [searchParams] = useSearchParams();

  const currentFeedback = createMemo(() => {
    const selected = props.selected();
    return selected ? props.feedback[selected] : null;
  });
  const setCurrentFeedback = () => {};

  const result = createMemo(() => {
    const selected = props.selected();
    return selected || selected === 0 ? props.results()[selected] : null;
  });

  let player!: HTMLIFrameElement;
  const url = () => {
    return `https://www.youtube-nocookie.com/embed/${result()?.video_id}?start=${
      result()?.start
    }&autoplay=1&rel=0`;
  };

  const submitFeedback = (feedback: Feedback) => {
    const selected = props.selected();
    if (selected && feedback === untrack(currentFeedback)) {
      console.log("hello world");
      try {
        postFeedback({
          feedback: feedback,
          query: searchParams.q!,
          result_id: result()?.video_id!,
        });
        // Implemenet selected as useSubmission
        props.setFeedback(selected, feedback);
      } catch {
        // console.log(error);
        alert("Failed to submit feedback. Please retry.");
      }
    }
  };

  return (
    <div class="theater" classList={{ slideDown: !!result() }}>
      <Show when={props.selected() !== null}>
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
        <div class="metaPanel">
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
                onclick={[submitFeedback, 1]}
                classList={{ selectedYES: currentFeedback() === 1 }}
              />
              <button
                id="btn-fb-no"
                type="button"
                onclick={[submitFeedback, -1]}
                classList={{ selectedNO: currentFeedback() === -1 }}
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
  load(props) {
    getResults(props.params.q);
  },
} satisfies RouteDefinition;

export default function App() {
  const [searchParams] = useSearchParams();
  const results = createAsyncStore(() => getResults(searchParams.q), { initialValue: [] });
  const [feedbackStore, setFeedbackStore] = createStore([] as Feedback[]);
  const [selected, setSelected] = createSignal<number | null>(null);
  // TODO: Refactor to push selected in results data structure
  createEffect(() => {
    setFeedbackStore(createFeedbackArray(results().length));
    setSelected(null);
  });

  return (
    <main>
      <header>
        <div class="tabsPanel">
          <img src="/img/logo.svg" alt="FastSearch logo" />
          <div class="tabs">
            <a href="/writeup/scope">PROJECT WRITEUP</a>
          </div>
        </div>
        <Search />
      </header>
      <div id="content" class="content">
        <ErrorBoundary fallback={(error) => <ErrorMessage error={error} />}>
          <Suspense>
            <Theater
              results={results}
              selected={selected}
              feedback={feedbackStore}
              setFeedback={setFeedbackStore}
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
 * - Try using html form get action for search submission
 * - Switch from list[index] to object[id] for results page ???
 * - Switch to manging state with `createStore`
 *
 * - Refactor css for css-in-js
 *    - Use css modules
 *    - Use css-in-js lib
 */

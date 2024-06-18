import {
  Accessor,
  Setter,
  InitializedResource,
  createSignal,
  createResource,
  createContext,
  useContext,
  createEffect,
} from "solid-js";
import { createStore, SetStoreFunction } from "solid-js/store";
import * as v from "valibot";

const ResultsSchema = v.array(
  v.object({
    id: v.string(),
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

async function fetchResults(query: string) {
  const resp = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query }),
  });
  if (!resp.ok) {
    throw new Error(`${resp.status} | ${resp.statusText}`);
  }
  const data = await resp.json();
  const results = v.parse(ResultsSchema, data);
  return results;
}

export type Feedback = -1 | null | 1;
export const initFeedback = (n: number) => Array(n).fill(null);

interface ContextProps {
  query: Accessor<string | null>;
  setQuery: Setter<string | null>;
  results: InitializedResource<v.InferOutput<typeof ResultsSchema>>;
  feedback: Feedback[];
  setFeedback: SetStoreFunction<Feedback[]>;
  selected: Accessor<number | null>;
  setSelected: Setter<number | null>;
}

const SearchContext = createContext<ContextProps>();

export function SearchContextProvider(props) {
  const [query, setQuery] = createSignal<string | null>(null);
  const [results] = createResource(query, fetchResults, { initialValue: [] });
  const [feedback, setFeedback] = createStore<Feedback[]>([]);
  const [selected, setSelected] = createSignal<number | null>(null);
  createEffect(() => {
    setFeedback(initFeedback(results().length));
    setSelected(null);
  });

  return (
    <SearchContext.Provider
      value={{
        query,
        setQuery,
        results,
        feedback,
        setFeedback,
        selected,
        setSelected,
      }}
    >
      {props.children}
    </SearchContext.Provider>
  );
}

export const useSearchContext = () => useContext(SearchContext)!;

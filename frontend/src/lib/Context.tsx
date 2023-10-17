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

export interface SearchResult {
  id: string;
  video_id: string;
  title: string;
  text: string;
  start: number;
  thumbnail: string;
  lesson: string | null;
  forum: string | null;
  course: string | null;
}

const fetchResults = async (query: string) => {
  return await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query }),
  }).then((response) => {
    if (response.ok) {
      return response.json() as Promise<SearchResult[]>;
    }
    throw new Error(`${response.status} | ${response.statusText}`);
  });
};

export type Feedback = -1 | null | 1;
export const initFeedback = (n: number) => Array(n).fill(null);

interface ContextProps {
  query: Accessor<string | null>;
  setQuery: Setter<string | null>;
  results: InitializedResource<SearchResult[]>;
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

import { onCleanup, onMount, startTransition } from "solid-js";
import { useSearchContext } from "~/lib/Context";
import "~/components/Search.css";

export default function SearchBar() {
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

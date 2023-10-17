import { For } from "solid-js";
import { secToHMS } from "~/lib/utils";
import { useSearchContext } from "~/lib/Context";
import "~/components/Results.css";

export default function Results() {
  const { results, selected, setSelected } = useSearchContext();

  const handleSelection = (index: number) => {
    window.scrollTo(0, 0);
    setSelected(index);
  };

  return (
    <ul id="results">
      <For each={results()}>
        {(result, i) => (
          <li
            onClick={[handleSelection, i]}
            classList={{ selected: selected() === i() }}
          >
            <div class="meta">
              <div class="vid">{result.title}</div>
              <div class="seg">
                <div>
                  <span>{secToHMS(result.start)}</span>
                  {result.text}
                </div>
              </div>
            </div>
            <img
              src={result.thumbnail}
              alt={`Thumbnail for ${result.title}.`}
            />
          </li>
        )}
      </For>
    </ul>
  );
}

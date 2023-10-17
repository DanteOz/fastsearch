import {
  createSignal,
  Show,
  untrack,
  createMemo,
  createEffect,
} from "solid-js";
import { useSearchContext, Feedback } from "~/lib/Context";
import { secToHMS } from "~/lib/utils.js";
import "~/components/Theater.css";

type feedbackProps = {
  feedback: number;
  query: string;
  result_id: string;
};

async function submitFeedback(props: feedbackProps) {
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

export default function Theater() {
  const { query, results, selected, feedback, setFeedback } =
    useSearchContext();
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

import { Title } from "@solidjs/meta";
import type { ParentProps } from "solid-js";

export function WriteupTitle(props: ParentProps) {
  return <Title>{props.children} | FastSearch</Title>;
}

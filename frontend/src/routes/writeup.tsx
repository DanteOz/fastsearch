import type { RouteDefinition } from "@solidjs/router";
import { WriteupNav } from "~/components/writeup/Nav";
import "~/styles/Writeup.css";

export default function Layout(props: RouteDefinition) {
  return (
    <>
      <WriteupNav />
      {props.children}
    </>
  );
}

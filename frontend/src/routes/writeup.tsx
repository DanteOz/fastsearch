import { Link } from "@solidjs/meta";
import type { RouteDefinition } from "@solidjs/router";
import { WriteupNav } from "~/components/writeup/Nav";
import "~/styles/writeup.css";

export default function Layout(props: RouteDefinition) {
  return (
    <>
      <Link rel="icon" type="image/x-icon" href="/img/writeup/favicon.ico" />
      <Link rel="icon" type="image/x-icns" href="/img/writeup/favicon.icns" />
      <Link rel="icon" type="image/png" href="/img/writeup/favicon_16x16.png" sizes="16x16" />
      <Link rel="icon" type="image/png" href="/img/writeup/favicon_32x32.png" sizes="32x32" />
      <Link rel="icon" type="image/png" href="/img/writeup/favicon_128x128.png" sizes="128x128" />
      <Link rel="icon" type="image/png" href="/img/writeup/favicon_256x256.png" sizes="256x256" />
      <Link rel="icon" type="image/png" href="/img/writeup/favicon_512x512.png" sizes="512x512" />
      <WriteupNav />
      {props.children}
    </>
  );
}

import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  ssr: false,
  vite: {
    server: {
      proxy: { "/api/": { target: "http://localhost:8000/", changeOrigin: false } },
    },
  },
});

import { defineConfig } from "@solidjs/start/config";

export default defineConfig({
  ssr: false,
  vite: {
    server: {
      compatibilityDate: "2025-05-11",
      proxy: {
        "/api/": {
          target: "http://localhost:8000/",
          changeOrigin: false,
        },
      },
    },
  },
});

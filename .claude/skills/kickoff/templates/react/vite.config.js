// Vite: build → web/dist (served by api.py), dev server proxies /api to the running API.
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": `http://localhost:${process.env.API_PORT || 8501}` } },
  test: { environment: "jsdom" },
});

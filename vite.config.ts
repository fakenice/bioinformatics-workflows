import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { buildApiPlugin } from "./vite-plugin-build-api.js";

export default defineConfig({
  plugins: [react(), tailwindcss(), buildApiPlugin()],
  base: "/bioinformatics-workflows/",
});

import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, "../backend/catalog/static/catalog/operations"),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, "src/main.tsx"),
      output: {
        entryFileNames: "operations.js",
        chunkFileNames: "[name].js",
        assetFileNames: "operations.[ext]"
      }
    }
  }
});

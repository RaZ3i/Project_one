import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const buildId = process.env.VITE_BUILD_ID || "dev";

export default defineConfig({
  plugins: [
    react(),
    {
      name: "inject-build-id",
      transformIndexHtml(html) {
        const meta = `    <meta name="build-id" content="${buildId}" />`;
        if (html.includes('name="build-id"')) {
          return html.replace(
            /<meta name="build-id" content="[^"]*"\s*\/?>/i,
            meta.trim(),
          );
        }
        return html.replace("</head>", `${meta}\n  </head>`);
      },
    },
  ],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "../backend/static",
    emptyOutDir: true,
  },
});

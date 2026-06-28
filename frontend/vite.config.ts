import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

function normalizeBasePath(basePath: string | undefined) {
  if (!basePath) {
    return "/";
  }

  const withLeadingSlash = basePath.startsWith("/") ? basePath : `/${basePath}`;
  return withLeadingSlash.endsWith("/") ? withLeadingSlash : `${withLeadingSlash}/`;
}

export default defineConfig({
  base: normalizeBasePath(process.env.VITE_BASE_PATH),
  plugins: [react()],
  test: {
    include: ["../tests/frontend/**/*.test.{ts,tsx}", "src/**/*.test.tsx"],
  },
});

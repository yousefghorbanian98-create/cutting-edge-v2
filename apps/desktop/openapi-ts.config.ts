import { defineConfig } from '@hey-api/openapi-ts';

/** S-012: regenerate with `pnpm exec openapi-ts -f openapi-ts.config.ts` from apps/desktop. */
export default defineConfig({
  input: './openapi.json',
  output: './src/lib/openapi',
  plugins: [
    '@hey-api/typescript',
    '@hey-api/sdk',
    {
      name: '@hey-api/client-fetch',
      // Same local core the desktop shell already talks to. Not an endpoint.
      baseUrl: 'http://127.0.0.1:8001',
    },
  ],
});

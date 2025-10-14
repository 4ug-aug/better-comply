import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input:
    'http://localhost/api/openapi.json',
  output: {
    format: 'prettier',
    lint: 'eslint',
    path: './src/queries',
  },
  plugins: [
    '@hey-api/schemas',
    {
      name: '@hey-api/client-axios',
      runtimeConfigPath: '@/api/axios-base', 
    },
    {
      dates: true,
      name: '@hey-api/transformers',
    },
    {
      enums: 'javascript',
      name: '@hey-api/typescript',
    },
    {
      name: '@hey-api/sdk',
      transformer: true,
    },
    '@tanstack/react-query',
  ],
});

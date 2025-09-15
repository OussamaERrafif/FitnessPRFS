import type { ConfigFile } from '@rtk-query/codegen-openapi'

const config: ConfigFile = {
  schemaFile: './openapi.json', // Path to your OpenAPI schema file
  apiFile: './lib/store/api.ts', // Path to your base API file
  apiImport: 'api',
  outputFile: './lib/store/generated-api.ts', // Where to generate the API
  exportName: 'generatedApi',
  hooks: true,
  tag: true,
  flattenArg: false,
}

export default config

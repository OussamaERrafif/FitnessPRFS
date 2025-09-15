const config = {
  schemaFile: './openapi.json', // Path to your OpenAPI schema file
  apiFile: './lib/store/api.ts', // Path to your base API file
  apiImport: 'api',
  outputFile: './lib/store/generated-api.ts', // Where to generate the API
  exportName: 'generatedApi',
  hooks: true,
  tag: true,
  flattenArg: false,
}

module.exports = config

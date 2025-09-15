# RTK Query Setup Guide

This document explains how the RTK Query code generation is set up for the FitnessPR API.

## Overview

RTK Query code generation automatically creates TypeScript hooks and types from our OpenAPI specification, ensuring type safety and consistency between the frontend and backend API.

## Files Structure

```
├── openapi.json                          # OpenAPI specification (source of truth)
├── rtk-query-codegen.config.js          # RTK Query codegen configuration
├── lib/store/
│   ├── api.ts                           # Base API configuration
│   ├── generated-api.ts                 # Generated API hooks and types (auto-generated)
│   ├── store.ts                         # Redux store configuration
│   └── hooks.ts                         # Redux hooks
└── app/api-test/                        # API testing page
    ├── page.tsx
    └── api-test-component.tsx
```

## Configuration

### Base API Configuration (`lib/store/api.ts`)
- Sets the base URL for API calls (`http://localhost:8000`)
- Configures headers and authentication
- Defines tag types for cache invalidation

### Codegen Configuration (`rtk-query-codegen.config.js`)
```javascript
{
  schemaFile: './openapi.json',           // Source OpenAPI file
  apiFile: './lib/store/api.ts',          // Base API file
  apiImport: 'api',                       // Import name for base API
  outputFile: './lib/store/generated-api.ts', // Generated output
  exportName: 'generatedApi',             // Export name
  hooks: true,                            // Generate React hooks
  tag: true,                              // Generate cache tags
  flattenArg: false,                      // Keep nested arguments
}
```

## Available Scripts

```bash
# Generate API from OpenAPI spec
npm run codegen

# Generate API with file watching (regenerates on OpenAPI changes)
npm run codegen:watch

# Alias for codegen
npm run api:generate

# Start dev server
npm run dev
```

## API Testing

The project includes a comprehensive API testing page at `/api-test` that allows you to:

### Test Available Endpoints
- Health check
- Exercises list
- Exercise categories
- Trainers list
- Authentication (register/login)

### View API Responses
- Real-time API response data
- Error handling and display
- Loading states

### Authentication Testing
- User registration form
- User login form
- Token handling

## Usage Examples

### Basic Query Hook
```typescript
import { useGetExercisesApiV1ExercisesGetQuery } from '@/lib/store/generated-api'

function ExercisesList() {
  const { data: exercises, error, isLoading } = useGetExercisesApiV1ExercisesGetQuery({
    skip: 0,
    limit: 10
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading exercises</div>
  
  return (
    <ul>
      {exercises?.map(exercise => (
        <li key={exercise.id}>{exercise.name}</li>
      ))}
    </ul>
  )
}
```

### Mutation Hook
```typescript
import { useRegisterApiV1AuthRegisterPostMutation } from '@/lib/store/generated-api'

function RegisterForm() {
  const [register, { isLoading, error }] = useRegisterApiV1AuthRegisterPostMutation()

  const handleSubmit = async (formData) => {
    try {
      const result = await register({
        registerRequest: formData
      }).unwrap()
      console.log('Registration successful:', result)
    } catch (err) {
      console.error('Registration failed:', err)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
    </form>
  )
}
```

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints Available

The generated API includes hooks for all endpoints defined in the OpenAPI spec:

### Authentication
- `useRegisterApiV1AuthRegisterPostMutation`
- `useLoginApiV1AuthLoginPostMutation`
- `useRefreshTokenApiV1AuthRefreshPostMutation`
- `useGetProfileApiV1AuthMeGetQuery`

### Exercises
- `useGetExercisesApiV1ExercisesGetQuery`
- `useCreateExerciseApiV1ExercisesPostMutation`
- `useGetExerciseCategoriesApiV1ExercisesCategoriesGetQuery`
- `useGetMuscleGroupsApiV1ExercisesMuscleGroupsGetQuery`

### Trainers
- `useGetAllTrainersApiV1TrainersGetQuery`
- `useCreateTrainerProfileApiV1TrainersPostMutation`
- `useGetMyTrainerProfileApiV1TrainersMeGetQuery`

### Clients
- `useListClientsApiV1ClientsGetQuery`
- `useCreateClientProfileApiV1ClientsPostMutation`
- `useGetMyClientProfileApiV1ClientsMeGetQuery`

### Programs
- `useGetProgramsApiV1ProgramsGetQuery`
- `useCreateProgramApiV1ProgramsPostMutation`

### Sessions
- `useGetSessionBookingsApiV1SessionsGetQuery`
- `useCreateSessionBookingApiV1SessionsPostMutation`

### And many more...

## Type Safety

All API calls are fully typed with TypeScript:
- Request parameters are typed
- Response data is typed
- Error responses are typed
- Enum values are properly typed

## Cache Management

RTK Query automatically manages cache invalidation using tags:
- `Authentication`
- `Users`
- `Clients`
- `Trainers`
- `Exercises`
- `Progress`
- `Programs`
- `Sessions`
- `Meals`
- `Notifications`

## Regenerating API

When the OpenAPI specification (`openapi.json`) is updated:

1. Run the code generation:
   ```bash
   npm run api:generate
   ```

2. The generated file (`lib/store/generated-api.ts`) will be updated automatically

3. Import and use the new hooks in your components

## Development Workflow

1. Update the backend API and regenerate the OpenAPI spec
2. Copy the updated `openapi.json` to the frontend project
3. Run `npm run api:generate` to regenerate the TypeScript hooks
4. Use the new hooks in your React components
5. Test the API using the `/api-test` page

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure `lib/store/generated-api.ts` is imported in your store configuration
2. **Type errors**: Regenerate the API after updating the OpenAPI spec
3. **Network errors**: Check that the backend API is running on the correct port
4. **Authentication errors**: Ensure proper token handling in the base API configuration

### Testing API Connection

Visit `/api-test` in your browser to test:
- API connectivity
- Individual endpoint responses
- Authentication flow
- Error handling

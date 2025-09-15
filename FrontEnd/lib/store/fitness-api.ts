import { api } from './api'

// Types for your fitness app
export interface Client {
  id: string
  name: string
  email: string
  phone?: string
  dateOfBirth?: string
  goals?: string
  currentWeight?: number
  targetWeight?: number
  activityLevel?: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
  createdAt: string
  updatedAt: string
}

export interface TrainingPlan {
  id: string
  name: string
  description?: string
  clientId?: string
  exercises: Exercise[]
  duration: number // in weeks
  frequency: number // sessions per week
  createdAt: string
  updatedAt: string
}

export interface Exercise {
  id: string
  name: string
  sets: number
  reps: string // e.g., "8-12" or "10"
  weight?: number
  duration?: number // in seconds
  restTime?: number // in seconds
  notes?: string
}

export interface MealPlan {
  id: string
  name: string
  description?: string
  clientId?: string
  meals: Meal[]
  totalCalories: number
  targetCalories: number
  createdAt: string
  updatedAt: string
}

export interface Meal {
  id: string
  name: string
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  foods: Food[]
  calories: number
  protein: number
  carbs: number
  fat: number
}

export interface Food {
  id: string
  name: string
  quantity: number
  unit: string
  calories: number
  protein: number
  carbs: number
  fat: number
}

// Enhanced API with fitness-specific endpoints
export const fitnessApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // Client endpoints
    getClients: builder.query<Client[], void>({
      query: () => 'clients',
      providesTags: ['Client'],
    }),
    getClient: builder.query<Client, string>({
      query: (id) => `clients/${id}`,
      providesTags: (result, error, id) => [{ type: 'Client', id }],
    }),
    createClient: builder.mutation<Client, Partial<Client>>({
      query: (newClient) => ({
        url: 'clients',
        method: 'POST',
        body: newClient,
      }),
      invalidatesTags: ['Client'],
    }),
    updateClient: builder.mutation<Client, { id: string; updates: Partial<Client> }>({
      query: ({ id, updates }) => ({
        url: `clients/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Client', id }],
    }),
    deleteClient: builder.mutation<void, string>({
      query: (id) => ({
        url: `clients/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Client'],
    }),

    // Training Plan endpoints
    getTrainingPlans: builder.query<TrainingPlan[], { clientId?: string }>({
      query: ({ clientId } = {}) => ({
        url: 'training-plans',
        params: clientId ? { clientId } : undefined,
      }),
      providesTags: ['TrainingPlan'],
    }),
    getTrainingPlan: builder.query<TrainingPlan, string>({
      query: (id) => `training-plans/${id}`,
      providesTags: (result, error, id) => [{ type: 'TrainingPlan', id }],
    }),
    createTrainingPlan: builder.mutation<TrainingPlan, Partial<TrainingPlan>>({
      query: (newPlan) => ({
        url: 'training-plans',
        method: 'POST',
        body: newPlan,
      }),
      invalidatesTags: ['TrainingPlan'],
    }),
    updateTrainingPlan: builder.mutation<TrainingPlan, { id: string; updates: Partial<TrainingPlan> }>({
      query: ({ id, updates }) => ({
        url: `training-plans/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'TrainingPlan', id }],
    }),
    deleteTrainingPlan: builder.mutation<void, string>({
      query: (id) => ({
        url: `training-plans/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['TrainingPlan'],
    }),

    // Meal Plan endpoints
    getMealPlans: builder.query<MealPlan[], { clientId?: string }>({
      query: ({ clientId } = {}) => ({
        url: 'meal-plans',
        params: clientId ? { clientId } : undefined,
      }),
      providesTags: ['MealPlan'],
    }),
    getMealPlan: builder.query<MealPlan, string>({
      query: (id) => `meal-plans/${id}`,
      providesTags: (result, error, id) => [{ type: 'MealPlan', id }],
    }),
    createMealPlan: builder.mutation<MealPlan, Partial<MealPlan>>({
      query: (newPlan) => ({
        url: 'meal-plans',
        method: 'POST',
        body: newPlan,
      }),
      invalidatesTags: ['MealPlan'],
    }),
    updateMealPlan: builder.mutation<MealPlan, { id: string; updates: Partial<MealPlan> }>({
      query: ({ id, updates }) => ({
        url: `meal-plans/${id}`,
        method: 'PUT',
        body: updates,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'MealPlan', id }],
    }),
    deleteMealPlan: builder.mutation<void, string>({
      query: (id) => ({
        url: `meal-plans/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['MealPlan'],
    }),
  }),
})

// Export hooks for usage in functional components
export const {
  // Client hooks
  useGetClientsQuery,
  useGetClientQuery,
  useCreateClientMutation,
  useUpdateClientMutation,
  useDeleteClientMutation,
  
  // Training Plan hooks
  useGetTrainingPlansQuery,
  useGetTrainingPlanQuery,
  useCreateTrainingPlanMutation,
  useUpdateTrainingPlanMutation,
  useDeleteTrainingPlanMutation,
  
  // Meal Plan hooks
  useGetMealPlansQuery,
  useGetMealPlanQuery,
  useCreateMealPlanMutation,
  useUpdateMealPlanMutation,
  useDeleteMealPlanMutation,
} = fitnessApi

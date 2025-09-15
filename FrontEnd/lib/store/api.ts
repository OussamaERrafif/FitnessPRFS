import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query'
import type { RootState } from './store'
import { logout, setTokens } from './authSlice'
import { getAuthTokens } from '@/lib/auth/cookies'

const baseQuery = fetchBaseQuery({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  prepareHeaders: (headers, { getState, endpoint }) => {
    console.log(`🔵 API Call: ${endpoint} - Preparing headers`)
    
    // Try to get token from Redux state first
    let token = (getState() as RootState).auth.accessToken
    const authState = (getState() as RootState).auth
    
    console.log(`🔍 Redux Auth State for ${endpoint}:`, {
      hasTokenInRedux: !!token,
      isAuthenticated: authState.isAuthenticated,
      expiresAt: authState.expiresAt,
      isExpired: authState.expiresAt ? authState.expiresAt <= Date.now() : 'no expiry',
      user: authState.user ? { email: authState.user.email, role: authState.user.role } : null
    })
    
    // If no token in Redux, try to get from cookies directly
    if (!token) {
      console.log(`⚠️ No token in Redux for ${endpoint}, checking cookies...`)
      const tokens = getAuthTokens()
      console.log(`🍪 Cookie tokens for ${endpoint}:`, {
        hasAccessToken: !!tokens.accessToken,
        hasRefreshToken: !!tokens.refreshToken,
        expiresAt: tokens.expiresAt,
        isValid: tokens.expiresAt && tokens.expiresAt > Date.now(),
        tokenPreview: tokens.accessToken ? tokens.accessToken.substring(0, 20) + '...' : 'none'
      })
      
      if (tokens.accessToken && tokens.expiresAt && tokens.expiresAt > Date.now()) {
        token = tokens.accessToken
        console.log(`✅ Using token from cookies for ${endpoint}`)
      }
    } else {
      console.log(`✅ Using token from Redux for ${endpoint}`)
    }
    
    if (token) {
      headers.set('authorization', `Bearer ${token}`)
      console.log(`🔑 Authorization header set for ${endpoint}:`, `Bearer ${token.substring(0, 20)}...`)
      
      // Let's also decode and check the token payload
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        console.log(`🔓 Token payload for ${endpoint}:`, {
          sub: payload.sub,
          exp: payload.exp,
          iat: payload.iat,
          expiresAt: new Date(payload.exp * 1000).toISOString(),
          isExpired: payload.exp * 1000 < Date.now(),
          timeUntilExpiry: Math.round((payload.exp * 1000 - Date.now()) / 1000 / 60) + ' minutes'
        })
      } catch (e) {
        console.error(`❌ Failed to decode token for ${endpoint}:`, e)
      }
    } else {
      console.error(`❌ No access token available for ${endpoint}`)
    }
    
    headers.set('content-type', 'application/json')
    headers.set('accept', 'application/json')
    
    console.log(`📋 Final headers for ${endpoint}:`, {
      authorization: headers.get('authorization') ? 'Bearer [token]' : 'MISSING',
      'content-type': headers.get('content-type'),
      'accept': headers.get('accept')
    })
    
    return headers
  },
})

const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  const url = typeof args === 'string' ? args : args.url
  console.log(`🚀 Making API request to: ${url}`)
  
  let result = await baseQuery(args, api, extraOptions)

  // Enhanced debugging for API responses
  console.log(`📡 API Response for ${url}:`, {
    status: result.error?.status || 'success',
    statusText: result.error?.status ? 'error' : 'ok',
    error: result.error?.data || null,
    hasData: !!result.data,
    meta: result.meta
  })

  if (result.error) {
    console.error(`❌ API Error for ${url}:`, {
      status: result.error.status,
      data: result.error.data,
      originalArgs: args
    })
  }

  if (result.error && result.error.status === 401) {
    console.log(`🔄 401 Unauthorized for ${url} - attempting token refresh`)
    // Try to get a new token
    const refreshToken = (api.getState() as RootState).auth.refreshToken
    
    if (refreshToken) {
      console.log('🔄 Attempting token refresh...')
      const refreshResult = await baseQuery(
        {
          url: '/api/v1/auth/refresh',
          method: 'POST',
          body: { refresh_token: refreshToken },
        },
        api,
        extraOptions
      )

      if (refreshResult.data) {
        const data = refreshResult.data as any
        console.log('✅ Token refresh successful')
        // Store the new tokens
        api.dispatch(setTokens({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          expiresIn: data.expires_in,
        }))
        
        // Retry the original query
        console.log(`🔄 Retrying original request to ${url}`)
        result = await baseQuery(args, api, extraOptions)
      } else {
        console.log('❌ Token refresh failed - logging out user')
        // Refresh failed, logout user
        api.dispatch(logout())
      }
    } else {
      console.log('❌ No refresh token available - logging out user')
      // No refresh token, logout user
      api.dispatch(logout())
    }
  } else if (result.error && result.error.status === 403) {
    console.error(`🚫 403 Forbidden for ${url}:`, {
      errorData: result.error.data,
      fullError: result.error,
      possibleCauses: [
        'User does not have permission to access this resource',
        'Token is valid but user role/permissions insufficient',
        'Resource-specific access control issue',
        'Backend API authentication/authorization issue'
      ]
    })
    
    // Let's also check what exactly the backend is saying
    console.error('🔍 Full 403 Error Details:', JSON.stringify(result.error, null, 2))
  }

  return result
}

// Define a service using a base URL and expected endpoints
export const api = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    'User',
    'Client', 
    'TrainingPlan',
    'MealPlan',
    'Report',
    'Payment',
    'Schedule',
    'Metric',
    'Feedback'
  ],
  endpoints: (builder) => ({
    // Example endpoint - replace with your actual API endpoints
    getUsers: builder.query<any[], void>({
      query: () => 'users',
      providesTags: ['User'],
    }),
  }),
})

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetUsersQuery } = api

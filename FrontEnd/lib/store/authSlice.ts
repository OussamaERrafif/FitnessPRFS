import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from './store'
import type { UserProfile } from './generated-api'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  expiresAt: number | null
  user: UserProfile | null
  isAuthenticated: boolean
}

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  expiresAt: null,
  user: null,
  isAuthenticated: false,
}

interface TokenPayload {
  accessToken: string
  refreshToken: string
  expiresIn: number
}

interface LoginPayload extends TokenPayload {
  user: UserProfile
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginSuccess: (state, action: PayloadAction<LoginPayload>) => {
      const { accessToken, refreshToken, expiresIn, user } = action.payload
      state.accessToken = accessToken
      state.refreshToken = refreshToken
      state.expiresAt = Date.now() + expiresIn * 1000
      state.user = user
      state.isAuthenticated = true
    },
    setTokens: (state, action: PayloadAction<TokenPayload>) => {
      const { accessToken, refreshToken, expiresIn } = action.payload
      state.accessToken = accessToken
      state.refreshToken = refreshToken
      state.expiresAt = Date.now() + expiresIn * 1000
      state.isAuthenticated = true
    },
    setUser: (state, action: PayloadAction<UserProfile>) => {
      state.user = action.payload
    },
    logout: (state) => {
      state.accessToken = null
      state.refreshToken = null
      state.expiresAt = null
      state.user = null
      state.isAuthenticated = false
    },
    clearTokens: (state) => {
      state.accessToken = null
      state.refreshToken = null
      state.expiresAt = null
      state.isAuthenticated = false
    },
  },
})

export const { loginSuccess, setTokens, setUser, logout, clearTokens } = authSlice.actions

// Selectors
export const selectAuth = (state: RootState) => state.auth
export const selectAccessToken = (state: RootState) => state.auth.accessToken
export const selectRefreshToken = (state: RootState) => state.auth.refreshToken
export const selectUser = (state: RootState) => state.auth.user
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated
export const selectTokenExpiry = (state: RootState) => state.auth.expiresAt

// Helper to check if token is expired or will expire soon (within 5 minutes)
export const selectIsTokenExpired = (state: RootState) => {
  const expiresAt = state.auth.expiresAt
  if (!expiresAt) return true
  return Date.now() >= expiresAt - 5 * 60 * 1000 // 5 minutes buffer
}

export default authSlice.reducer

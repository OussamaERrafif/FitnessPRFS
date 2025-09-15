'use client'

import { useEffect, useState, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '@/lib/store/hooks'
import { setTokens, logout } from '@/lib/store/authSlice'
import { getAuthTokens, setAuthTokens, clearAuthTokens } from '@/lib/auth/cookies'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const dispatch = useAppDispatch()
  const { accessToken, refreshToken, expiresAt } = useAppSelector((state) => state.auth)
  const [isInitialized, setIsInitialized] = useState(false)
  const hasInitialized = useRef(false)

  // Hydrate auth state from cookies on mount
  useEffect(() => {
    // Prevent double initialization in React Strict Mode
    if (hasInitialized.current) {
      console.log('🔄 AuthProvider: Skipping duplicate initialization (React Strict Mode)')
      return
    }
    hasInitialized.current = true
    
    console.log('🔄 AuthProvider: Starting initialization...')
    const tokens = getAuthTokens()
    
    console.log('🍪 AuthProvider: Cookie data:', {
      hasAccessToken: !!tokens.accessToken,
      accessTokenPreview: tokens.accessToken ? tokens.accessToken.substring(0, 30) + '...' : 'none',
      hasRefreshToken: !!tokens.refreshToken,
      refreshTokenPreview: tokens.refreshToken ? tokens.refreshToken.substring(0, 30) + '...' : 'none',
      expiresAt: tokens.expiresAt,
      expiresAtFormatted: tokens.expiresAt ? new Date(tokens.expiresAt).toLocaleString() : 'none',
      currentTime: Date.now(),
      currentTimeFormatted: new Date().toLocaleString(),
      isValid: tokens.expiresAt ? tokens.expiresAt > Date.now() : false,
      timeUntilExpiry: tokens.expiresAt ? Math.floor((tokens.expiresAt - Date.now()) / 1000) + 's' : 'n/a'
    })
    
    if (tokens.accessToken && tokens.refreshToken && tokens.expiresAt) {
      // Check if token is still valid
      if (tokens.expiresAt > Date.now()) {
        const expiresIn = Math.floor((tokens.expiresAt - Date.now()) / 1000)
        console.log('✅ AuthProvider: Setting valid tokens in Redux store', {
          expiresIn: expiresIn + 's',
          willExpireAt: new Date(Date.now() + expiresIn * 1000).toLocaleString()
        })
        dispatch(setTokens({
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
          expiresIn,
        }))
      } else {
        // Token expired, clear everything
        console.log('⚠️ AuthProvider: Token expired, clearing cookies', {
          expiredAt: new Date(tokens.expiresAt).toLocaleString(),
          expiredAgo: Math.floor((Date.now() - tokens.expiresAt) / 1000) + 's ago'
        })
        clearAuthTokens()
      }
    } else {
      console.log('❌ AuthProvider: No valid tokens found in cookies', {
        missingFields: {
          accessToken: !tokens.accessToken,
          refreshToken: !tokens.refreshToken,
          expiresAt: !tokens.expiresAt
        }
      })
    }
    
    // Mark as initialized immediately
    setIsInitialized(true)
    console.log('✅ AuthProvider: Initialization complete')
  }, [dispatch])

  // Sync cookies when auth state changes
  useEffect(() => {
    // Don't sync cookies during initial load to prevent clearing them
    if (!isInitialized) return
    
    console.log('🔄 AuthProvider: Syncing cookies with Redux state', {
      hasAccessToken: !!accessToken,
      hasRefreshToken: !!refreshToken,
      expiresAt,
      action: (accessToken && refreshToken && expiresAt) ? 'set' : 'clear'
    })
    
    if (accessToken && refreshToken && expiresAt) {
      const expiresIn = Math.floor((expiresAt - Date.now()) / 1000)
      console.log('🍪 AuthProvider: Setting auth tokens in cookies', {
        expiresIn: expiresIn + 's',
        expiresAtFormatted: new Date(expiresAt).toLocaleString()
      })
      setAuthTokens(accessToken, refreshToken, expiresIn)
    } else {
      // Only clear cookies if we had tokens and now we don't (logout scenario)
      // Don't clear during initial state when Redux is empty but cookies might be valid
      const currentCookies = getAuthTokens()
      if (currentCookies.accessToken && !accessToken) {
        console.log('⚠️ AuthProvider: Auth state cleared, removing cookies')
        clearAuthTokens()
      }
    }
  }, [accessToken, refreshToken, expiresAt, isInitialized])

  return <>{children}</>
}

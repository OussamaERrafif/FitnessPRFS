// Simple cookie management without external dependencies
export const authCookies = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  EXPIRES_AT: 'expires_at',
}

export function setCookie(name: string, value: string, days: number = 7) {
  if (typeof window === 'undefined') return

  const expires = new Date()
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
  
  // Remove secure flag for localhost development
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  const secureFlag = isLocalhost ? '' : '; secure'
  
  document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/${secureFlag}; samesite=lax`
}

export function getCookie(name: string): string | null {
  if (typeof window === 'undefined') return null

  const nameEQ = name + '='
  const ca = document.cookie.split(';')
  
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
  }
  
  return null
}

export function deleteCookie(name: string) {
  if (typeof window === 'undefined') return
  
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
}

export function setAuthTokens(accessToken: string, refreshToken: string, expiresIn: number) {
  const expiresAt = Date.now() + expiresIn * 1000
  
  setCookie(authCookies.ACCESS_TOKEN, accessToken, 7)
  setCookie(authCookies.REFRESH_TOKEN, refreshToken, 30) // Refresh token lasts longer
  setCookie(authCookies.EXPIRES_AT, expiresAt.toString(), 7)
}

export function getAuthTokens() {
  console.log('🍪 Getting auth tokens from cookies...')
  
  // Debug: log all cookies
  if (typeof window !== 'undefined') {
    console.log('🍪 All cookies:', document.cookie)
  }
  
  const tokens = {
    accessToken: getCookie(authCookies.ACCESS_TOKEN),
    refreshToken: getCookie(authCookies.REFRESH_TOKEN),
    expiresAt: getCookie(authCookies.EXPIRES_AT) ? parseInt(getCookie(authCookies.EXPIRES_AT)!) : null,
  }
  
  console.log('🍪 Parsed auth tokens:', {
    hasAccessToken: !!tokens.accessToken,
    accessTokenLength: tokens.accessToken?.length || 0,
    hasRefreshToken: !!tokens.refreshToken,
    refreshTokenLength: tokens.refreshToken?.length || 0,
    expiresAt: tokens.expiresAt,
    expiresAtDate: tokens.expiresAt ? new Date(tokens.expiresAt).toLocaleString() : 'none'
  })
  
  return tokens
}

export function clearAuthTokens() {
  deleteCookie(authCookies.ACCESS_TOKEN)
  deleteCookie(authCookies.REFRESH_TOKEN)
  deleteCookie(authCookies.EXPIRES_AT)
}

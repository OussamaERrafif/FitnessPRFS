import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const publicPaths = ['/login', '/register', '/api-test']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Check if the path is public
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path))
  
  // Allow API routes and public paths
  if (pathname.startsWith('/api') || isPublicPath) {
    return NextResponse.next()
  }
  
  // Check for auth tokens in cookies
  const accessToken = request.cookies.get('access_token')
  const expiresAt = request.cookies.get('expires_at')
  
  // If no token or token is expired, redirect to login
  if (!accessToken || !expiresAt || parseInt(expiresAt.value) <= Date.now()) {
    const loginUrl = new URL('/login', request.url)
    return NextResponse.redirect(loginUrl)
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
}

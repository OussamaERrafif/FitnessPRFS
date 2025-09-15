"use client"

import { useAppSelector } from '@/lib/store/hooks'
import { getAuthTokens } from '@/lib/auth/cookies'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

export default function AuthDebug() {
  const auth = useAppSelector((state) => state.auth)
  const [cookieTokens, setCookieTokens] = useState<any>(null)
  
  const checkCookies = () => {
    const tokens = getAuthTokens()
    setCookieTokens(tokens)
  }
  
  const logEverything = () => {
    console.log('🔍 COMPLETE AUTH DEBUG:')
    console.log('Redux State:', auth)
    console.log('Cookie Tokens:', getAuthTokens())
    console.log('All Cookies:', document.cookie)
    console.log('Local Storage:', { ...localStorage })
    console.log('Session Storage:', { ...sessionStorage })
  }
  
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Authentication Debug</h1>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Redux Auth State</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-64">
              {JSON.stringify(auth, null, 2)}
            </pre>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Cookie Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={checkCookies} className="mb-4">Check Cookies</Button>
            <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-64">
              {cookieTokens ? JSON.stringify(cookieTokens, null, 2) : 'Click "Check Cookies" to load'}
            </pre>
          </CardContent>
        </Card>
      </div>
      
      <div className="flex gap-2">
        <Button onClick={logEverything}>Log Everything to Console</Button>
        <Button onClick={() => {
          console.clear()
          console.log('🧹 Console cleared')
        }} variant="outline">Clear Console</Button>
      </div>
    </div>
  )
}

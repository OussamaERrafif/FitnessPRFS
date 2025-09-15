"use client"

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getAuthTokens, setAuthTokens, clearAuthTokens } from '@/lib/auth/cookies'

export default function ApiTest() {
  const [cookieData, setCookieData] = useState<any>(null)
  const [allCookies, setAllCookies] = useState<string>('')

  const refreshData = () => {
    const tokens = getAuthTokens()
    setCookieData(tokens)
    
    // Get all cookies
    if (typeof window !== 'undefined') {
      setAllCookies(document.cookie)
    }
  }

  useEffect(() => {
    refreshData()
  }, [])

  const testSetCookies = () => {
    setAuthTokens('test_access_token', 'test_refresh_token', 3600)
    setTimeout(refreshData, 100) // Small delay to ensure cookies are set
  }

  const testClearCookies = () => {
    clearAuthTokens()
    setTimeout(refreshData, 100)
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Cookie Debug Page</h1>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Auth Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-gray-100 p-4 rounded">
              {JSON.stringify(cookieData, null, 2)}
            </pre>
            <div className="mt-4 space-x-2">
              <Button onClick={testSetCookies} variant="outline">
                Test Set Cookies
              </Button>
              <Button onClick={testClearCookies} variant="outline">
                Clear Cookies
              </Button>
              <Button onClick={refreshData} variant="outline">
                Refresh
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>All Cookies</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-gray-100 p-4 rounded whitespace-pre-wrap">
              {allCookies || 'No cookies found'}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

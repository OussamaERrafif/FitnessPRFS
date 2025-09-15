"use client"

import { useAppSelector } from '@/lib/store/hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function AuthStatus() {
  const auth = useAppSelector((state) => state.auth)
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Auth Status 
          <Badge variant={auth.isAuthenticated ? "default" : "destructive"}>
            {auth.isAuthenticated ? "Authenticated" : "Not Authenticated"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm">
          <div>
            <strong>Access Token:</strong> {auth.accessToken ? 'Present' : 'Missing'}
          </div>
          <div>
            <strong>Refresh Token:</strong> {auth.refreshToken ? 'Present' : 'Missing'}
          </div>
          <div>
            <strong>Expires At:</strong> {auth.expiresAt ? new Date(auth.expiresAt).toLocaleString() : 'Not set'}
          </div>
          <div>
            <strong>User:</strong> {auth.user ? `${auth.user.email} (${auth.user.role})` : 'No user data'}
          </div>
          <div>
            <strong>Is Expired:</strong> {auth.expiresAt ? (auth.expiresAt <= Date.now() ? 'Yes' : 'No') : 'Unknown'}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

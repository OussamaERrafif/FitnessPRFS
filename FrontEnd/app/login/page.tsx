'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import Link from 'next/link'
import { useAppDispatch } from '@/lib/store/hooks'
import { loginSuccess } from '@/lib/store/authSlice'
import { generatedApi } from '@/lib/store/generated-api'

export default function LoginPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [formErrors, setFormErrors] = useState({
    email: '',
    password: '',
  })

  const [loginMutation, { isLoading }] = generatedApi.useLoginApiV1AuthLoginPostMutation()

  const validateForm = () => {
    const errors = {
      email: '',
      password: '',
    }

    if (!formData.email.trim()) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email address'
    }

    if (!formData.password.trim()) {
      errors.password = 'Password is required'
    }

    setFormErrors(errors)
    return !errors.email && !errors.password
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when user starts typing
    if (formErrors[field as keyof typeof formErrors]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    console.log('🔐 Login form submitted')
    
    if (!validateForm()) {
      console.log('❌ Form validation failed')
      return
    }

    try {
      setError(null)
      
      console.log('🚀 Calling login API...')
      
      // Call login API
      const loginResult = await loginMutation({
        loginRequest: {
          email: formData.email,
          password: formData.password,
        },
      }).unwrap()

      console.log('✅ Login API successful:', loginResult)

      // Extract data from login response - it already contains user info
      const { 
        access_token, 
        refresh_token, 
        expires_in,
        user_id,
        email,
        username,
        full_name,
        role,
        is_verified
      } = loginResult

      // Create user profile object from login response
      const userProfile = {
        id: user_id,
        email: email,
        username: username,
        full_name: full_name,
        role: role,
        is_active: true,
        is_verified: is_verified,
        phone: null,
        date_of_birth: null,
        gender: null,
        height: null,
        avatar_url: null,
        bio: null,
        created_at: new Date().toISOString(),
        last_login: new Date().toISOString(),
      }

      console.log('📝 Dispatching login success to Redux with user:', userProfile)

      // Store everything in Redux (and sync to cookies via AuthProvider)
      dispatch(loginSuccess({
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresIn: expires_in,
        user: userProfile,
      }))

      console.log('🎯 About to redirect to dashboard...')

      // Small delay to ensure Redux state is updated
      setTimeout(() => {
        console.log('🔄 Executing redirect now')
        router.push('/')
      }, 100)
      
    } catch (err: any) {
      console.error('Login failed:', err)
      setError(err.data?.detail || 'Login failed. Please check your credentials.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
          <CardDescription>Sign in to your TrainerPro account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className={formErrors.email ? 'border-destructive' : ''}
              />
              {formErrors.email && (
                <p className="text-sm text-destructive">{formErrors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className={formErrors.password ? 'border-destructive' : ''}
              />
              {formErrors.password && (
                <p className="text-sm text-destructive">{formErrors.password}</p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            <div className="text-center text-sm text-muted-foreground">
              Don't have an account?{' '}
              <Link href="/register" className="text-primary hover:underline">
                Sign up
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

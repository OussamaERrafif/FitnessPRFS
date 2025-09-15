'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Loader2, CheckCircle, XCircle, Activity } from 'lucide-react'

// Import the generated API hooks
import { 
  useHealthCheckApiHealthGetQuery,
  useGetExercisesApiV1ExercisesGetQuery,
  useRegisterApiV1AuthRegisterPostMutation,
  useLoginApiV1AuthLoginPostMutation,
  useGetAllTrainersApiV1TrainersGetQuery,
  useGetExerciseCategoriesApiV1ExercisesCategoriesGetQuery
} from '@/lib/store/generated-api'

export default function ApiTestComponent() {
  const [testResults, setTestResults] = useState<Record<string, any>>({})
  const [loginCredentials, setLoginCredentials] = useState({ email: '', password: '' })
  const [registerData, setRegisterData] = useState({ 
    email: '', 
    password: '', 
    username: '', 
    full_name: '' 
  })

  // Health check query
  const { 
    data: healthData, 
    error: healthError, 
    isLoading: healthLoading, 
    refetch: refetchHealth 
  } = useHealthCheckApiHealthGetQuery()

  // Exercises query
  const { 
    data: exercisesData, 
    error: exercisesError, 
    isLoading: exercisesLoading, 
    refetch: refetchExercises 
  } = useGetExercisesApiV1ExercisesGetQuery({})

  // Exercise categories query
  const { 
    data: categoriesData, 
    error: categoriesError, 
    isLoading: categoriesLoading, 
    refetch: refetchCategories 
  } = useGetExerciseCategoriesApiV1ExercisesCategoriesGetQuery()

  // Trainers query
  const { 
    data: trainersData, 
    error: trainersError, 
    isLoading: trainersLoading, 
    refetch: refetchTrainers 
  } = useGetAllTrainersApiV1TrainersGetQuery({})

  // Auth mutations
  const [registerUser, { isLoading: registerLoading }] = useRegisterApiV1AuthRegisterPostMutation()
  const [loginUser, { isLoading: loginLoading }] = useLoginApiV1AuthLoginPostMutation()

  const handleRegister = async () => {
    try {
      const result = await registerUser({ registerRequest: registerData }).unwrap()
      setTestResults(prev => ({ ...prev, register: { success: true, data: result } }))
    } catch (error) {
      setTestResults(prev => ({ ...prev, register: { success: false, error } }))
    }
  }

  const handleLogin = async () => {
    try {
      const result = await loginUser({ loginRequest: loginCredentials }).unwrap()
      setTestResults(prev => ({ ...prev, login: { success: true, data: result } }))
    } catch (error) {
      setTestResults(prev => ({ ...prev, login: { success: false, error } }))
    }
  }

  const getStatusIcon = (loading: boolean, error: any, data: any) => {
    if (loading) return <Loader2 className="h-4 w-4 animate-spin" />
    if (error) return <XCircle className="h-4 w-4 text-red-500" />
    if (data) return <CheckCircle className="h-4 w-4 text-green-500" />
    return <Activity className="h-4 w-4 text-gray-500" />
  }

  const getStatusBadge = (loading: boolean, error: any, data: any) => {
    if (loading) return <Badge variant="secondary">Loading</Badge>
    if (error) return <Badge variant="destructive">Error</Badge>
    if (data) return <Badge variant="default">Success</Badge>
    return <Badge variant="outline">Not tested</Badge>
  }

  return (
    <div className="space-y-6">
      {/* API Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            API Connection Status
          </CardTitle>
          <CardDescription>
            Test the connection to the FitnessPR API endpoints
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Health Check */}
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Health Check</span>
                {getStatusIcon(healthLoading, healthError, healthData)}
              </div>
              {getStatusBadge(healthLoading, healthError, healthData)}
              <Button 
                size="sm" 
                variant="outline" 
                className="w-full mt-2" 
                onClick={() => refetchHealth()}
                disabled={healthLoading}
              >
                Test
              </Button>
            </Card>

            {/* Exercises */}
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Exercises</span>
                {getStatusIcon(exercisesLoading, exercisesError, exercisesData)}
              </div>
              {getStatusBadge(exercisesLoading, exercisesError, exercisesData)}
              <Button 
                size="sm" 
                variant="outline" 
                className="w-full mt-2" 
                onClick={() => refetchExercises()}
                disabled={exercisesLoading}
              >
                Test
              </Button>
            </Card>

            {/* Categories */}
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Categories</span>
                {getStatusIcon(categoriesLoading, categoriesError, categoriesData)}
              </div>
              {getStatusBadge(categoriesLoading, categoriesError, categoriesData)}
              <Button 
                size="sm" 
                variant="outline" 
                className="w-full mt-2" 
                onClick={() => refetchCategories()}
                disabled={categoriesLoading}
              >
                Test
              </Button>
            </Card>

            {/* Trainers */}
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Trainers</span>
                {getStatusIcon(trainersLoading, trainersError, trainersData)}
              </div>
              {getStatusBadge(trainersLoading, trainersError, trainersData)}
              <Button 
                size="sm" 
                variant="outline" 
                className="w-full mt-2" 
                onClick={() => refetchTrainers()}
                disabled={trainersLoading}
              >
                Test
              </Button>
            </Card>
          </div>
        </CardContent>
      </Card>

      {/* API Data and Testing */}
      <Tabs defaultValue="responses" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="responses">API Responses</TabsTrigger>
          <TabsTrigger value="auth">Authentication</TabsTrigger>
          <TabsTrigger value="errors">Errors & Debug</TabsTrigger>
        </TabsList>

        <TabsContent value="responses" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Health Data */}
            <Card>
              <CardHeader>
                <CardTitle>Health Check Response</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-32">
                  <pre className="text-sm">
                    {healthData ? JSON.stringify(healthData, null, 2) : 'No data'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Exercises Data */}
            <Card>
              <CardHeader>
                <CardTitle>Exercises Response</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-32">
                  <pre className="text-sm">
                    {exercisesData ? JSON.stringify(exercisesData.slice(0, 3), null, 2) : 'No data'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Categories Data */}
            <Card>
              <CardHeader>
                <CardTitle>Categories Response</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-32">
                  <pre className="text-sm">
                    {categoriesData ? JSON.stringify(categoriesData, null, 2) : 'No data'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Trainers Data */}
            <Card>
              <CardHeader>
                <CardTitle>Trainers Response</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-32">
                  <pre className="text-sm">
                    {trainersData ? JSON.stringify(trainersData.slice(0, 2), null, 2) : 'No data'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="auth" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Register */}
            <Card>
              <CardHeader>
                <CardTitle>User Registration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="reg-email">Email</Label>
                  <Input
                    id="reg-email"
                    type="email"
                    value={registerData.email}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="test@example.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reg-username">Username</Label>
                  <Input
                    id="reg-username"
                    value={registerData.username}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, username: e.target.value }))}
                    placeholder="testuser"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reg-name">Full Name</Label>
                  <Input
                    id="reg-name"
                    value={registerData.full_name}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, full_name: e.target.value }))}
                    placeholder="Test User"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reg-password">Password</Label>
                  <Input
                    id="reg-password"
                    type="password"
                    value={registerData.password}
                    onChange={(e) => setRegisterData(prev => ({ ...prev, password: e.target.value }))}
                    placeholder="password123"
                  />
                </div>
                <Button 
                  onClick={handleRegister} 
                  disabled={registerLoading}
                  className="w-full"
                >
                  {registerLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Register
                </Button>
                {testResults.register && (
                  <ScrollArea className="h-24 mt-2">
                    <pre className="text-sm">
                      {JSON.stringify(testResults.register, null, 2)}
                    </pre>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>

            {/* Login */}
            <Card>
              <CardHeader>
                <CardTitle>User Login</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    value={loginCredentials.email}
                    onChange={(e) => setLoginCredentials(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="test@example.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    value={loginCredentials.password}
                    onChange={(e) => setLoginCredentials(prev => ({ ...prev, password: e.target.value }))}
                    placeholder="password123"
                  />
                </div>
                <Button 
                  onClick={handleLogin} 
                  disabled={loginLoading}
                  className="w-full"
                >
                  {loginLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Login
                </Button>
                {testResults.login && (
                  <ScrollArea className="h-24 mt-2">
                    <pre className="text-sm">
                      {JSON.stringify(testResults.login, null, 2)}
                    </pre>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="errors" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Health Error */}
            {healthError && (
              <Card>
                <CardHeader>
                  <CardTitle>Health Check Error</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-32">
                    <pre className="text-sm text-red-600">
                      {JSON.stringify(healthError, null, 2)}
                    </pre>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            {/* Exercises Error */}
            {exercisesError && (
              <Card>
                <CardHeader>
                  <CardTitle>Exercises Error</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-32">
                    <pre className="text-sm text-red-600">
                      {JSON.stringify(exercisesError, null, 2)}
                    </pre>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            {/* Categories Error */}
            {categoriesError && (
              <Card>
                <CardHeader>
                  <CardTitle>Categories Error</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-32">
                    <pre className="text-sm text-red-600">
                      {JSON.stringify(categoriesError, null, 2)}
                    </pre>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            {/* Trainers Error */}
            {trainersError && (
              <Card>
                <CardHeader>
                  <CardTitle>Trainers Error</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-32">
                    <pre className="text-sm text-red-600">
                      {JSON.stringify(trainersError, null, 2)}
                    </pre>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

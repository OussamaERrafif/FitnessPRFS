"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import { ErrorState } from "@/components/ui/error-state"
import {
  ArrowLeft,
  MessageSquare,
  Calendar,
  FileText,
  Eye,
  EyeOff,
  RefreshCw,
  TrendingUp,
  Target,
  CheckCircle,
  User,
  Dumbbell,
  CreditCard,
  Shield,
} from "lucide-react"
import {
  useGetClientProfileApiV1ClientsClientIdGetQuery,
  useGetClientStatsApiV1ClientsClientIdStatsGetQuery,
  useGetClientProgressLogsApiV1ProgressClientClientIdGetQuery,
  useGetUserApiV1UsersUserIdGetQuery,
} from "@/lib/store/generated-api"
import Link from "next/link"

// Helper function to get initials for avatar fallback
const getInitials = (name: string) => {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
}

// Helper function to get client status
const getClientStatus = (client: any) => {
  if (!client?.is_membership_active) return "inactive"
  return "active"
}

// Helper function to get status color
const getStatusColor = (status: string) => {
  switch (status) {
    case "active":
      return "bg-green-100 text-green-800 border-green-200"
    case "needs-attention":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "inactive":
      return "bg-gray-100 text-gray-800 border-gray-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

export default function ClientDetailPage() {
  const params = useParams()
  const clientId = Number(params.id)
  const [showPin, setShowPin] = useState(false)

  // Fetch client data
  const {
    data: client,
    error: clientError,
    isLoading: clientLoading,
    refetch: refetchClient
  } = useGetClientProfileApiV1ClientsClientIdGetQuery({ clientId })

  // Fetch user data when client is available
  const {
    data: user,
    error: userError,
    isLoading: userLoading,
    refetch: refetchUser
  } = useGetUserApiV1UsersUserIdGetQuery(
    { userId: client?.user_id || 0 },
    { skip: !client?.user_id }
  )

  // Fetch client stats
  const {
    data: stats,
    error: statsError,
    isLoading: statsLoading,
    refetch: refetchStats
  } = useGetClientStatsApiV1ClientsClientIdStatsGetQuery({ clientId })

  // Fetch progress logs
  const {
    data: progressLogs,
    error: progressError,
    isLoading: progressLoading,
    refetch: refetchProgress
  } = useGetClientProgressLogsApiV1ProgressClientClientIdGetQuery({ 
    clientId,
    limit: 20 
  })

  const isLoading = clientLoading || statsLoading || userLoading
  const hasError = clientError || statsError || userError

  // Handle loading state
  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-8 w-8 bg-gray-200 rounded animate-pulse" />
          <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
        </div>
        <LoadingSkeleton type="detail" />
      </div>
    )
  }

  // Handle error state
  if (hasError || !client) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <Link href="/clients">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Clients
            </Button>
          </Link>
        </div>
        <ErrorState
          title="Failed to load client"
          message="There was an error loading the client data. Please try again."
          onRetry={() => {
            refetchClient()
            refetchStats()
            refetchProgress()
            refetchUser()
          }}
        />
      </div>
    )
  }

  const status = getClientStatus(client)
  const userName = user?.full_name || user?.email || 'Unknown Client'

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/clients">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Clients
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => {
            refetchClient()
            refetchStats()
            refetchProgress()
            refetchUser()
          }}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Client Header Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarImage src={user?.avatar_url || "/placeholder-user.jpg"} />
                <AvatarFallback className="text-lg">{getInitials(userName)}</AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-2xl font-bold">{userName}</h1>
                <p className="text-muted-foreground">{user?.email}</p>
                {user?.phone && (
                  <p className="text-muted-foreground">{user.phone}</p>
                )}
                <div className="flex gap-2 mt-2">
                  <Badge className={getStatusColor(status)}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </Badge>
                  {client.membership_type && (
                    <Badge variant="outline">{client.membership_type}</Badge>
                  )}
                  {client.fitness_goals && client.fitness_goals.length > 0 && (
                    <Badge variant="outline">{client.fitness_goals[0]}</Badge>
                  )}
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <MessageSquare className="w-4 h-4 mr-2" />
                Message
              </Button>
              <Button size="sm" variant="outline">
                <Calendar className="w-4 h-4 mr-2" />
                Schedule
              </Button>
              <Button size="sm">
                <FileText className="w-4 h-4 mr-2" />
                Edit Profile
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <Dumbbell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_sessions || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.completed_sessions || 0} completed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Weight Progress</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_weight_change ? `${stats.total_weight_change > 0 ? '+' : ''}${stats.total_weight_change}kg` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Current: {client.current_weight ? `${client.current_weight}kg` : 'Not set'}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Programs</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_programs || 0}</div>
            <p className="text-xs text-muted-foreground">
              Programs enrolled
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Streak</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.current_streak_days || 0}</div>
            <p className="text-xs text-muted-foreground">
              Days active
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed information */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="progress">Progress</TabsTrigger>
          <TabsTrigger value="programs">Programs</TabsTrigger>
          <TabsTrigger value="sessions">Sessions</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Member Since</span>
                  <span className="font-medium">
                    {client.created_at ? new Date(client.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
                {client.age && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Age</span>
                    <span className="font-medium">{client.age} years</span>
                  </div>
                )}
                {client.height && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Height</span>
                    <span className="font-medium">{client.height} cm</span>
                  </div>
                )}
                {client.fitness_level && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Fitness Level</span>
                    <span className="font-medium capitalize">{client.fitness_level}</span>
                  </div>
                )}
                {client.activity_level && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Activity Level</span>
                    <span className="font-medium capitalize">{client.activity_level}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Fitness Goals */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Fitness Goals
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {client.fitness_goals && client.fitness_goals.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {client.fitness_goals.map((goal, index) => (
                      <Badge key={index} variant="outline">{goal}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No goals set</p>
                )}
                {client.current_weight && client.target_weight && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Weight Goal Progress</span>
                      <span>{client.current_weight}kg / {client.target_weight}kg</span>
                    </div>
                    <Progress value={Math.min(100, (1 - Math.abs(client.current_weight - client.target_weight) / client.current_weight) * 100)} />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Membership Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5" />
                  Membership
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status</span>
                  <Badge className={client.is_membership_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                    {client.is_membership_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                {client.membership_type && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Plan</span>
                    <span className="font-medium">{client.membership_type}</span>
                  </div>
                )}
                {client.membership_start_date && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Start Date</span>
                    <span className="font-medium">
                      {new Date(client.membership_start_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {client.membership_end_date && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">End Date</span>
                    <span className="font-medium">
                      {new Date(client.membership_end_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* PIN Access */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  PIN Access
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Client PIN</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-medium">
                      {showPin ? (client.pin_code || "Not set") : "••••••"}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowPin(!showPin)}
                    >
                      {showPin ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full">
                  Regenerate PIN
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="progress" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Progress Logs</CardTitle>
              <CardDescription>
                Latest workout and measurement entries
              </CardDescription>
            </CardHeader>
            <CardContent>
              {progressLoading && <div>Loading progress data...</div>}
              {progressError && <div className="text-red-600">Error loading progress data</div>}
              {progressLogs && progressLogs.length > 0 ? (
                <div className="space-y-4">
                  {progressLogs.slice(0, 10).map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <p className="font-medium">{log.exercise_name || 'Exercise'}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(log.workout_date).toLocaleDateString()}
                        </p>
                        {log.notes && (
                          <p className="text-sm text-muted-foreground">{log.notes}</p>
                        )}
                      </div>
                      <div className="text-right">
                        {log.weight && <p className="font-medium">{log.weight}kg</p>}
                        {log.reps && <p className="text-sm text-muted-foreground">{log.reps} reps</p>}
                        {log.duration && <p className="text-sm text-muted-foreground">{Math.floor(log.duration / 60)}min</p>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No progress logs available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="programs">
          <Card>
            <CardHeader>
              <CardTitle>Active Programs</CardTitle>
              <CardDescription>Current training and meal plans</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Program details will be loaded here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sessions">
          <Card>
            <CardHeader>
              <CardTitle>Session History</CardTitle>
              <CardDescription>Past and upcoming training sessions</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Session history will be loaded here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Client Settings</CardTitle>
              <CardDescription>Manage client preferences and access</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Settings panel will be implemented here</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

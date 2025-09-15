"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import { ErrorState } from "@/components/ui/error-state"
import {
  ArrowLeft,
  Calendar,
  RefreshCw,
  TrendingUp,
  Target,
  CheckCircle,
  Clock,
  Dumbbell,
  Play,
  Pause,
  Edit,
  BarChart3,
  Award,
} from "lucide-react"
import {
  useGetProgramApiV1ProgramsProgramIdGetQuery,
  useGetProgramExercisesApiV1ProgramsProgramIdExercisesGetQuery,
  useGetUserApiV1UsersUserIdGetQuery,
} from "@/lib/store/generated-api"
import Link from "next/link"

// Helper function to get status color
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "active":
      return "bg-green-100 text-green-800 border-green-200"
    case "completed":
      return "bg-blue-100 text-blue-800 border-blue-200"
    case "paused":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "cancelled":
      return "bg-red-100 text-red-800 border-red-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

// Helper function to get difficulty color
const getDifficultyColor = (difficulty: string) => {
  switch (difficulty.toLowerCase()) {
    case "beginner":
      return "bg-green-100 text-green-800"
    case "intermediate":
      return "bg-yellow-100 text-yellow-800"
    case "advanced":
      return "bg-red-100 text-red-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

// Helper function to get program type color
const getProgramTypeColor = (type: string) => {
  const colors = {
    'strength': 'bg-red-100 text-red-800',
    'cardio': 'bg-blue-100 text-blue-800',
    'flexibility': 'bg-green-100 text-green-800',
    'powerlifting': 'bg-purple-100 text-purple-800',
    'bodybuilding': 'bg-orange-100 text-orange-800',
    'crossfit': 'bg-yellow-100 text-yellow-800'
  }
  return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

export default function TrainingPlanDetailPage() {
  const params = useParams()
  const programId = Number(params.id)
  const [activeTab, setActiveTab] = useState("overview")

  // Fetch program data
  const {
    data: program,
    error: programError,
    isLoading: programLoading,
    refetch: refetchProgram
  } = useGetProgramApiV1ProgramsProgramIdGetQuery({ programId })

  // Fetch program exercises
  const {
    data: exercises,
    error: exercisesError,
    isLoading: exercisesLoading,
    refetch: refetchExercises
  } = useGetProgramExercisesApiV1ProgramsProgramIdExercisesGetQuery({ programId })

  // Fetch client data when program is available
  const {
    data: client,
    error: clientError,
    isLoading: clientLoading,
    refetch: refetchClient
  } = useGetUserApiV1UsersUserIdGetQuery(
    { userId: program?.client_id || 0 },
    { skip: !program?.client_id }
  )

  // Fetch trainer data when program is available
  const {
    data: trainer,
    error: trainerError,
    isLoading: trainerLoading,
    refetch: refetchTrainer
  } = useGetUserApiV1UsersUserIdGetQuery(
    { userId: program?.trainer_id || 0 },
    { skip: !program?.trainer_id }
  )

  const isLoading = programLoading || exercisesLoading || clientLoading || trainerLoading
  const hasError = programError || exercisesError || clientError || trainerError

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
  if (hasError || !program) {
    return (
      <div className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <Link href="/training-plans">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Training Plans
            </Button>
          </Link>
        </div>
        <ErrorState
          title="Failed to load training plan"
          message="There was an error loading the training plan data. Please try again."
          onRetry={() => {
            refetchProgram()
            refetchExercises()
            refetchClient()
            refetchTrainer()
          }}
        />
      </div>
    )
  }

  const completionPercentage = program.completion_percentage || 0
  const weeksRemaining = Math.max(0, program.duration_weeks - program.current_week)

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/training-plans">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Training Plans
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => {
            refetchProgram()
            refetchExercises()
            refetchClient()
            refetchTrainer()
          }}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Program Header Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="space-y-4">
              <div>
                <h1 className="text-3xl font-bold">{program.name}</h1>
                <p className="text-muted-foreground mt-2">{program.description}</p>
                <div className="flex gap-2 mt-3">
                  <Badge className={getStatusColor(program.status)}>
                    {program.status.charAt(0).toUpperCase() + program.status.slice(1)}
                  </Badge>
                  <Badge className={getProgramTypeColor(program.program_type)}>
                    {program.program_type.replace('_', ' ')}
                  </Badge>
                  <Badge className={getDifficultyColor(program.difficulty_level)}>
                    {program.difficulty_level.charAt(0).toUpperCase() + program.difficulty_level.slice(1)}
                  </Badge>
                  {program.is_template && (
                    <Badge variant="outline">Template</Badge>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Client</p>
                  <p className="font-medium">{program.client_name || client?.full_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Trainer</p>
                  <p className="font-medium">{program.trainer_name || trainer?.full_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">{program.duration_weeks} weeks</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Sessions/Week</p>
                  <p className="font-medium">{program.sessions_per_week}</p>
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button size="sm" variant="outline">
                <Edit className="w-4 h-4 mr-2" />
                Edit Program
              </Button>
              <Button size="sm">
                {program.status === "active" ? (
                  <>
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Start
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Progress Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completionPercentage}%</div>
            <Progress value={completionPercentage} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-2">
              Week {program.current_week} of {program.duration_weeks}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sessions</CardTitle>
            <Dumbbell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {program.sessions_completed}/{program.total_sessions || 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              {program.sessions_completed} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Time Remaining</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{weeksRemaining}</div>
            <p className="text-xs text-muted-foreground">
              Weeks remaining
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Program Status</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{program.status}</div>
            <p className="text-xs text-muted-foreground">
              Started {new Date(program.start_date).toLocaleDateString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed information */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="exercises">Exercises</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
          <TabsTrigger value="progress">Progress</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Program Goals */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Program Goals
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {program.goals && program.goals.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {program.goals.map((goal, index) => (
                      <Badge key={index} variant="outline">{goal}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No specific goals set</p>
                )}
                
                {program.special_instructions && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Special Instructions</h4>
                    <p className="text-sm text-muted-foreground">{program.special_instructions}</p>
                  </div>
                )}
                
                {program.notes && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Notes</h4>
                    <p className="text-sm text-muted-foreground">{program.notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Target Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Target Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {program.target_metrics ? (
                  <div className="space-y-2">
                    {Object.entries(program.target_metrics).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-muted-foreground capitalize">{key.replace('_', ' ')}</span>
                        <span className="font-medium">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No specific targets set</p>
                )}
              </CardContent>
            </Card>

            {/* Program Timeline */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Timeline
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Start Date</span>
                  <span className="font-medium">
                    {new Date(program.start_date).toLocaleDateString()}
                  </span>
                </div>
                {program.end_date && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Planned End</span>
                    <span className="font-medium">
                      {new Date(program.end_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {program.actual_end_date && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Actual End</span>
                    <span className="font-medium">
                      {new Date(program.actual_end_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Week</span>
                  <span className="font-medium">{program.current_week}</span>
                </div>
              </CardContent>
            </Card>

            {/* Payment Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5" />
                  Program Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Payment Status</span>
                  <Badge className={program.is_paid ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                    {program.is_paid ? "Paid" : "Unpaid"}
                  </Badge>
                </div>
                {program.price && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Price</span>
                    <span className="font-medium">${program.price}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created</span>
                  <span className="font-medium">
                    {new Date(program.created_at).toLocaleDateString()}
                  </span>
                </div>
                {program.updated_at && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Updated</span>
                    <span className="font-medium">
                      {new Date(program.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="exercises">
          <Card>
            <CardHeader>
              <CardTitle>Program Exercises</CardTitle>
              <CardDescription>
                Exercises included in this training program
              </CardDescription>
            </CardHeader>
            <CardContent>
              {exercisesLoading && <div>Loading exercises...</div>}
              {exercisesError && <div className="text-red-600">Error loading exercises</div>}
              {exercises && exercises.length > 0 ? (
                <div className="space-y-4">
                  {exercises.map((exercise, index) => (
                    <div key={exercise.id || index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <p className="font-medium">{exercise.name || 'Exercise'}</p>
                        <p className="text-sm text-muted-foreground">
                          {exercise.muscle_groups?.join(', ') || 'No muscle groups specified'}
                        </p>
                        {exercise.description && (
                          <p className="text-sm text-muted-foreground mt-1">{exercise.description}</p>
                        )}
                      </div>
                      <div className="text-right">
                        {exercise.difficulty_level && (
                          <Badge className={getDifficultyColor(exercise.difficulty_level)}>
                            {exercise.difficulty_level}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No exercises found for this program</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule">
          <Card>
            <CardHeader>
              <CardTitle>Weekly Schedule</CardTitle>
              <CardDescription>Program workout schedule by week</CardDescription>
            </CardHeader>
            <CardContent>
              {program.weekly_schedule ? (
                <div className="space-y-4">
                  {Object.entries(program.weekly_schedule).map(([key, value]) => (
                    <div key={key} className="p-4 border rounded-lg">
                      <h4 className="font-medium capitalize mb-2">{key.replace('_', ' ')}</h4>
                      <pre className="text-sm text-muted-foreground overflow-auto">
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No schedule data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="progress">
          <Card>
            <CardHeader>
              <CardTitle>Progress Tracking</CardTitle>
              <CardDescription>Client progress and performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Progress tracking features will be implemented here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Program Settings</CardTitle>
              <CardDescription>Manage program configuration and preferences</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Program settings will be implemented here</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
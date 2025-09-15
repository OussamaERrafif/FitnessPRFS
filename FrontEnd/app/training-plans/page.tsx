"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import { ErrorState } from "@/components/ui/error-state"
import {
  Search,
  Plus,
  RefreshCw,
  Dumbbell,
  Calendar,
  Target,
  TrendingUp,
  Clock,
  ChevronLeft,
  ChevronRight,
  Grid3X3,
  List,
  Copy,
  Edit,
  Trash2,
  Play,
  Users,
  Activity
} from "lucide-react"
import {
  useGetProgramsApiV1ProgramsGetQuery,
  ProgramResponse,
} from "@/lib/store/generated-api"

// Helper functions
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "active":
      return "bg-green-100 text-green-800 border-green-200"
    case "completed":
      return "bg-blue-100 text-blue-800 border-blue-200"
    case "paused":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "draft":
      return "bg-gray-100 text-gray-800 border-gray-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

const getDifficultyColor = (difficulty: string) => {
  const colors = {
    'beginner': 'bg-green-100 text-green-800',
    'intermediate': 'bg-yellow-100 text-yellow-800',
    'advanced': 'bg-red-100 text-red-800'
  }
  return colors[difficulty as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

const getPlanTypeColor = (type: string) => {
  const colors = {
    'strength_training': 'bg-red-100 text-red-800',
    'weight_loss': 'bg-orange-100 text-orange-800',
    'muscle_building': 'bg-purple-100 text-purple-800',
    'endurance': 'bg-blue-100 text-blue-800',
    'flexibility': 'bg-green-100 text-green-800',
    'sports_specific': 'bg-indigo-100 text-indigo-800',
    'rehabilitation': 'bg-yellow-100 text-yellow-800',
    'general_fitness': 'bg-gray-100 text-gray-800'
  }
  return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

export default function TrainingPlansPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [difficultyFilter, setDifficultyFilter] = useState<string>("")
  const [planTypeFilter, setPlanTypeFilter] = useState<string>("")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 12

  // Fetch training plans data
  const {
    data: trainingPlans,
    error,
    isLoading,
    refetch
  } = useGetProgramsApiV1ProgramsGetQuery({})

  // Filter training plans
  const filteredTrainingPlans = useMemo(() => {
    if (!trainingPlans) return []
    
    return trainingPlans.filter((plan: ProgramResponse) => {
      const matchesSearch = !searchTerm || 
        plan.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plan.client_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plan.description?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = !statusFilter || plan.status === statusFilter
      const matchesDifficulty = !difficultyFilter || plan.difficulty_level === difficultyFilter
      const matchesType = !planTypeFilter || plan.program_type === planTypeFilter
      
      return matchesSearch && matchesStatus && matchesDifficulty && matchesType
    })
  }, [trainingPlans, searchTerm, statusFilter, difficultyFilter, planTypeFilter])

  // Pagination
  const totalPages = Math.ceil(filteredTrainingPlans.length / itemsPerPage)
  const paginatedTrainingPlans = filteredTrainingPlans.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // Calculate stats
  const stats = useMemo(() => {
    if (!trainingPlans) return { total: 0, active: 0, templates: 0, thisWeek: 0 }
    
    const total = trainingPlans.length
    const active = trainingPlans.filter((p: ProgramResponse) => p.status === 'active').length
    const templates = trainingPlans.filter((p: ProgramResponse) => p.is_template).length
    
    const now = new Date()
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const thisWeek = trainingPlans.filter((p: ProgramResponse) => {
      const createdDate = new Date(p.created_at)
      return createdDate >= weekAgo
    }).length
    
    return { total, active, templates, thisWeek }
  }, [trainingPlans])

  // Handle loading state
  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 w-96 bg-gray-200 rounded animate-pulse" />
          </div>
          <div className="h-9 w-32 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded animate-pulse" />
          ))}
        </div>
        <LoadingSkeleton type="cards" />
      </div>
    )
  }

  // Handle error state
  if (error) {
    return (
      <div className="p-6">
        <ErrorState
          title="Failed to load training plans"
          message="There was an error loading the training plan data. Please try again."
          onRetry={refetch}
        />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Training Plans</h1>
          <p className="text-muted-foreground">Create and manage workout programs for your clients</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={refetch}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button className="bg-primary hover:bg-primary/90">
            <Plus className="w-4 h-4 mr-2" />
            Create Plan
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Plans</CardTitle>
            <Dumbbell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">
              All training plans created
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Plans</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-muted-foreground">
              Currently in progress
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Templates</CardTitle>
            <Copy className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.templates}</div>
            <p className="text-xs text-muted-foreground">
              Reusable templates
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Week</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.thisWeek}</div>
            <p className="text-xs text-muted-foreground">
              Plans created this week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and View Controls */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search training plans by name, client, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Levels</SelectItem>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={planTypeFilter} onValueChange={setPlanTypeFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Plan Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="strength_training">Strength Training</SelectItem>
                <SelectItem value="weight_loss">Weight Loss</SelectItem>
                <SelectItem value="muscle_building">Muscle Building</SelectItem>
                <SelectItem value="endurance">Endurance</SelectItem>
                <SelectItem value="flexibility">Flexibility</SelectItem>
                <SelectItem value="sports_specific">Sports Specific</SelectItem>
                <SelectItem value="rehabilitation">Rehabilitation</SelectItem>
                <SelectItem value="general_fitness">General Fitness</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex items-center space-x-1 border rounded-md">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("grid")}
                className="rounded-r-none"
              >
                <Grid3X3 className="w-4 h-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className="rounded-l-none"
              >
                <List className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Training Plans Display */}
      {filteredTrainingPlans.length > 0 ? (
        <>
          {viewMode === "grid" ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {paginatedTrainingPlans.map((plan: ProgramResponse, index: number) => (
                <Card key={plan.id} className="cursor-pointer hover:shadow-lg transition-shadow duration-200 animate-in slide-in-from-bottom-4" 
                      style={{ animationDelay: `${index * 50}ms` }}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1 flex-1">
                        <CardTitle className="text-lg">{plan.name}</CardTitle>
                        {plan.client_name && (
                          <p className="text-sm text-muted-foreground">
                            Client: {plan.client_name}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-col gap-1 items-end">
                        {plan.is_template && (
                          <Badge variant="outline" className="text-xs">
                            Template
                          </Badge>
                        )}
                        <Badge className={getStatusColor(plan.status)}>
                          {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Plan Type</span>
                      <Badge className={getPlanTypeColor(plan.program_type)}>
                        {plan.program_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Difficulty</span>
                      <Badge className={getDifficultyColor(plan.difficulty_level)}>
                        {plan.difficulty_level.charAt(0).toUpperCase() + plan.difficulty_level.slice(1)}
                      </Badge>
                    </div>
                    
                    {plan.duration_weeks && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Duration</span>
                        <span className="font-medium">{plan.duration_weeks} weeks</span>
                      </div>
                    )}
                    
                    {plan.sessions_per_week && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Sessions/Week</span>
                        <span className="font-medium">{plan.sessions_per_week}</span>
                      </div>
                    )}
                    
                    {plan.completion_percentage > 0 && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Progress</span>
                        <span className="font-medium">{plan.completion_percentage}%</span>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Created</span>
                      <span>{formatDate(plan.created_at)}</span>
                    </div>
                    
                    {plan.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {plan.description}
                      </p>
                    )}
                    
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Play className="w-4 h-4 mr-1" />
                        Start
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-0">
                <div className="divide-y">
                  {paginatedTrainingPlans.map((plan: ProgramResponse, index: number) => (
                    <div key={plan.id} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors cursor-pointer animate-in slide-in-from-bottom-2"
                         style={{ animationDelay: `${index * 25}ms` }}>
                      <div className="flex items-center space-x-4 flex-1">
                        <div className="flex-1">
                          <h3 className="font-medium">{plan.name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            {plan.client_name && (
                              <span className="text-sm text-muted-foreground">
                                Client: {plan.client_name}
                              </span>
                            )}
                            <Badge className={getPlanTypeColor(plan.program_type)} variant="outline">
                              {plan.program_type.replace('_', ' ')}
                            </Badge>
                            <Badge className={getDifficultyColor(plan.difficulty_level)} variant="outline">
                              {plan.difficulty_level}
                            </Badge>
                            {plan.is_template && (
                              <Badge variant="outline">Template</Badge>
                            )}
                          </div>
                        </div>
                        
                        <div className="text-center">
                          <div className="font-medium">{plan.duration_weeks || 0}</div>
                          <div className="text-xs text-muted-foreground">weeks</div>
                        </div>
                        
                        <div className="text-center">
                          <div className="font-medium">{plan.sessions_per_week || 0}</div>
                          <div className="text-xs text-muted-foreground">sessions/week</div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        <Badge className={getStatusColor(plan.status)}>
                          {plan.status.charAt(0).toUpperCase() + plan.status.slice(1)}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {formatDate(plan.created_at)}
                        </span>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm">
                            <Play className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Copy className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredTrainingPlans.length)} of {filteredTrainingPlans.length} training plans
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>
                <div className="text-sm font-medium">
                  Page {currentPage} of {totalPages}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <Dumbbell className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">No training plans found</h3>
            <p className="text-sm text-muted-foreground">
              {searchTerm || statusFilter || difficultyFilter || planTypeFilter
                ? "Try adjusting your search or filters to see more results."
                : "Get started by creating your first training plan."}
            </p>
            {!searchTerm && !statusFilter && !difficultyFilter && !planTypeFilter && (
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Training Plan
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

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
import { useSelector } from "react-redux"
import { RootState } from "@/lib/store/store"
import {
  Search,
  Filter,
  Grid3X3,
  List,
  Plus,
  RefreshCw,
  User,
  Calendar,
  Activity,
  TrendingUp,
  Users,
  UserCheck,
  Clock,
  ChevronLeft,
  ChevronRight
} from "lucide-react"
import {
  useGetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetQuery,
  ClientResponse,
} from "@/lib/store/generated-api"
import Link from "next/link"

// Helper functions
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "active":
      return "bg-green-100 text-green-800 border-green-200"
    case "inactive":
      return "bg-gray-100 text-gray-800 border-gray-200"
    case "pending":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "suspended":
      return "bg-red-100 text-red-800 border-red-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

export default function ClientsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 12

  // Get trainer ID from auth state
  const { user } = useSelector((state: RootState) => state.auth)
  console.log('🏠 Clients Page - Current user:', user)

  // Fetch clients data for this trainer
  const {
    data: clients,
    error,
    isLoading,
    refetch
  } = useGetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetQuery(
    { trainerId: user?.id || 0 },
    { skip: !user?.id }
  )

  // Debug the API call
  console.log('🏠 Clients Page - API call state:', {
    trainerId: user?.id,
    isLoading,
    hasData: !!clients,
    dataLength: clients?.length || 0,
    error: error ? {
      status: 'status' in error ? error.status : 'unknown',
      data: 'data' in error ? error.data : error,
    } : null,
    timestamp: new Date().toISOString()
  })

  // Filter clients based on search and status
  const filteredClients = useMemo(() => {
    if (!clients) return []
    
    return clients.filter((client: ClientResponse) => {
      const matchesSearch = !searchTerm || 
        client.id.toString().includes(searchTerm.toLowerCase()) ||
        client.fitness_level?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.fitness_goals?.some(goal => goal.toLowerCase().includes(searchTerm.toLowerCase()))
      
      const matchesStatus = statusFilter === 'all' || !statusFilter || client.is_membership_active === (statusFilter === 'active')
      
      return matchesSearch && matchesStatus
    })
  }, [clients, searchTerm, statusFilter])

  // Pagination
  const totalPages = Math.ceil(filteredClients.length / itemsPerPage)
  const paginatedClients = filteredClients.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // Calculate stats
  const stats = useMemo(() => {
    if (!clients) return { total: 0, active: 0, inactive: 0, newThisMonth: 0 }
    
    const total = clients.length
    const active = clients.filter((c: ClientResponse) => c.is_membership_active).length
    const inactive = clients.filter((c: ClientResponse) => !c.is_membership_active).length
    
    const now = new Date()
    const newThisMonth = clients.filter((c: ClientResponse) => {
      const createdDate = new Date(c.created_at)
      return createdDate.getMonth() === now.getMonth() && 
             createdDate.getFullYear() === now.getFullYear()
    }).length
    
    return { total, active, inactive, newThisMonth }
  }, [clients])

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
          title="Failed to load clients"
          message="There was an error loading the client data. Please try again."
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
          <h1 className="text-3xl font-bold text-foreground">Clients</h1>
          <p className="text-muted-foreground">Manage your training clients and their progress</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={refetch}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button className="bg-primary hover:bg-primary/90">
            <Plus className="w-4 h-4 mr-2" />
            Add Client
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">
              All registered clients
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Clients</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-muted-foreground">
              Currently training
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inactive Clients</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.inactive}</div>
            <p className="text-xs text-muted-foreground">
              Not currently active
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New This Month</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.newThisMonth}</div>
            <p className="text-xs text-muted-foreground">
              Recent sign-ups
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
                  placeholder="Search clients by name or email..."
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
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
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

      {/* Clients Display */}
      {filteredClients.length > 0 ? (
        <>
          {viewMode === "grid" ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {paginatedClients.map((client, index) => (
                <Link key={client.id} href={`/clients/${client.id}`}>
                  <Card className="cursor-pointer hover:shadow-lg transition-shadow duration-200 animate-in slide-in-from-bottom-4" 
                        style={{ animationDelay: `${index * 50}ms` }}>
                    <CardContent className="pt-6">
                      <div className="flex items-center space-x-4">
                        <Avatar className="w-12 h-12">
                          <AvatarImage src="/placeholder-user.jpg" />
                          <AvatarFallback>
                            {`C${client.id}`}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium truncate">Client #{client.id}</h3>
                          <p className="text-sm text-muted-foreground truncate">
                            {client.fitness_level ? `Fitness Level: ${client.fitness_level}` : 'Fitness Profile'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="mt-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Status</span>
                          <Badge className={client.is_membership_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                            {client.is_membership_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                        
                        {client.fitness_goals && client.fitness_goals.length > 0 && (
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">Goals</span>
                            <span className="text-sm truncate">{client.fitness_goals[0]}</span>
                          </div>
                        )}
                        
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Joined</span>
                          <span className="text-sm">{formatDate(client.created_at)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-0">
                <div className="divide-y">
                  {paginatedClients.map((client, index) => (
                    <Link key={client.id} href={`/clients/${client.id}`}>
                      <div className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors cursor-pointer animate-in slide-in-from-bottom-2"
                           style={{ animationDelay: `${index * 25}ms` }}>
                        <div className="flex items-center space-x-4">
                          <Avatar className="w-10 h-10">
                            <AvatarImage src="/placeholder-user.jpg" />
                            <AvatarFallback>
                              {`C${client.id}`}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <h3 className="font-medium">Client #{client.id}</h3>
                            <p className="text-sm text-muted-foreground">
                              {client.fitness_level ? `Level: ${client.fitness_level}` : 'Fitness Profile'}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          {client.fitness_level && (
                            <span className="text-sm text-muted-foreground">Level: {client.fitness_level}</span>
                          )}
                          <Badge className={client.is_membership_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                            {client.is_membership_active ? 'Active' : 'Inactive'}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {formatDate(client.created_at)}
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredClients.length)} of {filteredClients.length} clients
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
            <User className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-muted-foreground mb-2">No clients found</h3>
            <p className="text-sm text-muted-foreground">
              {searchTerm || (statusFilter && statusFilter !== 'all')
                ? "Try adjusting your search or filters to see more results."
                : "Get started by adding your first client."}
            </p>
            {!searchTerm && (!statusFilter || statusFilter === 'all') && (
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Client
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

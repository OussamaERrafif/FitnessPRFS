"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import { ErrorState } from "@/components/ui/error-state"
import { Calendar, Plus, Clock, Users, ChevronLeft, ChevronRight, Filter, RefreshCw, CheckCircle, AlertCircle, XCircle } from "lucide-react"
import {
  useGetSessionBookingsApiV1SessionsGetQuery,
  useCreateSessionBookingApiV1SessionsPostMutation,
  useUpdateSessionBookingApiV1SessionsBookingIdPutMutation,
  useCancelSessionBookingApiV1SessionsBookingIdCancelPostMutation,
  useConfirmSessionBookingApiV1SessionsBookingIdConfirmPostMutation,
  useListClientsApiV1ClientsGetQuery,
  useGetUserApiV1UsersUserIdGetQuery,
  SessionBookingResponse,
  SessionBookingCreate,
} from "@/lib/store/generated-api"

const timeSlots = Array.from({ length: 14 }, (_, i) => {
  const hour = i + 6 // Start from 6 AM
  return `${hour.toString().padStart(2, "0")}:00`
})

const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

// Helper function to get status color
const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "confirmed":
      return "bg-green-100 text-green-800 border-green-200"
    case "pending":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "cancelled":
      return "bg-red-100 text-red-800 border-red-200"
    case "completed":
      return "bg-blue-100 text-blue-800 border-blue-200"
    case "no_show":
      return "bg-gray-100 text-gray-800 border-gray-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

// Helper function to get session type color
const getSessionTypeColor = (type: string) => {
  const colors = {
    'personal_training': 'bg-blue-500',
    'group_training': 'bg-purple-500',
    'consultation': 'bg-green-500',
    'assessment': 'bg-orange-500',
    'nutrition': 'bg-yellow-500',
    'physio': 'bg-red-500'
  }
  return colors[type as keyof typeof colors] || 'bg-gray-500'
}

// Helper function to format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Helper function to format time
const formatTime = (dateTimeString: string) => {
  return new Date(dateTimeString).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

export default function SchedulingPage() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<"week" | "day" | "month">("week")
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<{ date: string; time: string } | null>(null)
  const [selectedSession, setSelectedSession] = useState<SessionBookingResponse | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [sessionTypeFilter, setSessionTypeFilter] = useState<string>("")
  
  // New session form data
  const [newSession, setNewSession] = useState<Partial<SessionBookingCreate>>({
    session_type: "",
    title: "",
    description: "",
    duration_minutes: 60,
    location: "",
    client_id: undefined,
    trainer_id: 1, // Assume current user is trainer with ID 1
  })

  // API queries
  const {
    data: sessions,
    error: sessionsError,
    isLoading: sessionsLoading,
    refetch: refetchSessions
  } = useGetSessionBookingsApiV1SessionsGetQuery({})

  const {
    data: clients,
    error: clientsError,
    isLoading: clientsLoading
  } = useListClientsApiV1ClientsGetQuery({})

  // API mutations
  const [createSession] = useCreateSessionBookingApiV1SessionsPostMutation()
  const [updateSession] = useUpdateSessionBookingApiV1SessionsBookingIdPutMutation()
  const [cancelSession] = useCancelSessionBookingApiV1SessionsBookingIdCancelPostMutation()
  const [confirmSession] = useConfirmSessionBookingApiV1SessionsBookingIdConfirmPostMutation()

  const isLoading = sessionsLoading || clientsLoading
  const hasError = sessionsError || clientsError

  // Filter sessions based on status and type
  const filteredSessions = useMemo(() => {
    if (!sessions) return []
    
    return sessions.filter(session => {
      const statusMatch = !statusFilter || session.status === statusFilter
      const typeMatch = !sessionTypeFilter || session.session_type === sessionTypeFilter
      return statusMatch && typeMatch
    })
  }, [sessions, statusFilter, sessionTypeFilter])

  // Get current week dates
  const getWeekDates = (date: Date) => {
    const week = []
    const startOfWeek = new Date(date)
    const day = startOfWeek.getDay()
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1) // Adjust for Monday start
    startOfWeek.setDate(diff)

    for (let i = 0; i < 7; i++) {
      const currentDay = new Date(startOfWeek)
      currentDay.setDate(startOfWeek.getDate() + i)
      week.push(currentDay)
    }
    return week
  }

  const weekDates = getWeekDates(currentDate)

  const navigateWeek = (direction: "prev" | "next") => {
    const newDate = new Date(currentDate)
    newDate.setDate(currentDate.getDate() + (direction === "next" ? 7 : -7))
    setCurrentDate(newDate)
  }

  const getSessionsForDate = (date: Date) => {
    const dateString = date.toISOString().split("T")[0]
    return filteredSessions.filter((session) => {
      const sessionDate = new Date(session.scheduled_start).toISOString().split("T")[0]
      return sessionDate === dateString
    })
  }

  const getSessionPosition = (startTime: string, duration: number) => {
    const startDate = new Date(startTime)
    const hours = startDate.getHours()
    const minutes = startDate.getMinutes()
    const startMinutes = (hours - 6) * 60 + minutes // 6 AM is our start time
    const top = (startMinutes / 60) * 60 // 60px per hour
    const height = (duration / 60) * 60
    return { top, height }
  }

  const handleTimeSlotClick = (date: Date, time: string) => {
    const dateTimeString = `${date.toISOString().split("T")[0]}T${time}:00`
    const endTime = new Date(dateTimeString)
    endTime.setHours(endTime.getHours() + 1) // Default 1 hour duration
    
    setNewSession({
      ...newSession,
      scheduled_start: dateTimeString,
      scheduled_end: endTime.toISOString(),
    })
    setSelectedTimeSlot({
      date: date.toISOString().split("T")[0],
      time,
    })
    setShowBookingModal(true)
  }

  const handleCreateSession = async () => {
    if (!newSession.session_type || !newSession.scheduled_start || !newSession.scheduled_end) {
      return
    }

    try {
      await createSession({
        sessionBookingCreate: newSession as SessionBookingCreate
      }).unwrap()
      
      setShowBookingModal(false)
      setNewSession({
        session_type: "",
        title: "",
        description: "",
        duration_minutes: 60,
        location: "",
        client_id: undefined,
        trainer_id: 1,
      })
      refetchSessions()
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const handleUpdateSession = async (sessionId: number, updates: Partial<SessionBookingResponse>) => {
    try {
      await updateSession({
        bookingId: sessionId,
        sessionBookingUpdate: updates
      }).unwrap()
      refetchSessions()
    } catch (error) {
      console.error('Failed to update session:', error)
    }
  }

  const handleCancelSession = async (sessionId: number) => {
    try {
      await cancelSession({ bookingId: sessionId }).unwrap()
      setSelectedSession(null)
      refetchSessions()
    } catch (error) {
      console.error('Failed to cancel session:', error)
    }
  }

  const handleConfirmSession = async (sessionId: number) => {
    try {
      await confirmSession({ bookingId: sessionId }).unwrap()
      setSelectedSession(null)
      refetchSessions()
    } catch (error) {
      console.error('Failed to confirm session:', error)
    }
  }

  // Calculate today's stats
  const todaySessions = useMemo(() => {
    const today = new Date().toISOString().split("T")[0]
    return filteredSessions.filter(session => {
      const sessionDate = new Date(session.scheduled_start).toISOString().split("T")[0]
      return sessionDate === today
    })
  }, [filteredSessions])

  const todayStats = useMemo(() => {
    const totalSessions = todaySessions.length
    const totalHours = todaySessions.reduce((sum, session) => sum + (session.duration_minutes || 60), 0) / 60
    const uniqueClients = new Set(todaySessions.map(session => session.client_id)).size
    
    return { totalSessions, totalHours, uniqueClients }
  }, [todaySessions])

  // Handle loading state
  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 w-96 bg-gray-200 rounded animate-pulse" />
          </div>
          <div className="flex gap-2">
            <div className="h-9 w-20 bg-gray-200 rounded animate-pulse" />
            <div className="h-9 w-32 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
        <LoadingSkeleton type="table" />
      </div>
    )
  }

  // Handle error state
  if (hasError) {
    return (
      <div className="p-6">
        <ErrorState
          title="Failed to load scheduling data"
          message="There was an error loading the session data. Please try again."
          onRetry={() => {
            refetchSessions()
          }}
        />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Scheduling</h1>
          <p className="text-muted-foreground">Manage your training sessions and availability</p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="confirmed">Confirmed</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
              <SelectItem value="no_show">No Show</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={sessionTypeFilter} onValueChange={setSessionTypeFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Session Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Types</SelectItem>
              <SelectItem value="personal_training">Personal Training</SelectItem>
              <SelectItem value="group_training">Group Training</SelectItem>
              <SelectItem value="consultation">Consultation</SelectItem>
              <SelectItem value="assessment">Assessment</SelectItem>
              <SelectItem value="nutrition">Nutrition</SelectItem>
              <SelectItem value="physio">Physiotherapy</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" onClick={refetchSessions}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          
          <Dialog open={showBookingModal} onOpenChange={setShowBookingModal}>
            <DialogTrigger asChild>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Book Session
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Book New Session</DialogTitle>
                <DialogDescription>Schedule a new training session or consultation</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="client">Client</Label>
                  <Select 
                    value={newSession.client_id?.toString() || ""} 
                    onValueChange={(value) => setNewSession({...newSession, client_id: value ? Number(value) : undefined})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select client" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients?.map((client) => (
                        <SelectItem key={client.id} value={client.id.toString()}>
                          {client.full_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="date">Date</Label>
                    <Input
                      type="date"
                      value={newSession.scheduled_start ? new Date(newSession.scheduled_start).toISOString().split("T")[0] : ""}
                      onChange={(e) => {
                        const date = e.target.value
                        const currentTime = newSession.scheduled_start ? new Date(newSession.scheduled_start).toTimeString().split(" ")[0] : "09:00:00"
                        const newStartTime = `${date}T${currentTime}`
                        const newEndTime = new Date(newStartTime)
                        newEndTime.setMinutes(newEndTime.getMinutes() + (newSession.duration_minutes || 60))
                        setNewSession({
                          ...newSession,
                          scheduled_start: newStartTime,
                          scheduled_end: newEndTime.toISOString()
                        })
                      }}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="time">Time</Label>
                    <Input
                      type="time"
                      value={newSession.scheduled_start ? new Date(newSession.scheduled_start).toTimeString().slice(0, 5) : ""}
                      onChange={(e) => {
                        const time = e.target.value
                        const currentDate = newSession.scheduled_start ? new Date(newSession.scheduled_start).toISOString().split("T")[0] : new Date().toISOString().split("T")[0]
                        const newStartTime = `${currentDate}T${time}:00`
                        const newEndTime = new Date(newStartTime)
                        newEndTime.setMinutes(newEndTime.getMinutes() + (newSession.duration_minutes || 60))
                        setNewSession({
                          ...newSession,
                          scheduled_start: newStartTime,
                          scheduled_end: newEndTime.toISOString()
                        })
                      }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="session-type">Session Type</Label>
                  <Select value={newSession.session_type} onValueChange={(value) => setNewSession({...newSession, session_type: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="personal_training">Personal Training</SelectItem>
                      <SelectItem value="group_training">Group Training</SelectItem>
                      <SelectItem value="consultation">Consultation</SelectItem>
                      <SelectItem value="assessment">Assessment</SelectItem>
                      <SelectItem value="nutrition">Nutrition</SelectItem>
                      <SelectItem value="physio">Physiotherapy</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="duration">Duration (minutes)</Label>
                  <Select 
                    value={newSession.duration_minutes?.toString() || "60"} 
                    onValueChange={(value) => {
                      const duration = Number(value)
                      setNewSession({...newSession, duration_minutes: duration})
                      // Update end time if start time is set
                      if (newSession.scheduled_start) {
                        const newEndTime = new Date(newSession.scheduled_start)
                        newEndTime.setMinutes(newEndTime.getMinutes() + duration)
                        setNewSession(prev => ({...prev, scheduled_end: newEndTime.toISOString()}))
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select duration" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="45">45 minutes</SelectItem>
                      <SelectItem value="60">60 minutes</SelectItem>
                      <SelectItem value="90">90 minutes</SelectItem>
                      <SelectItem value="120">120 minutes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="title">Title</Label>
                  <Input 
                    placeholder="Session title" 
                    value={newSession.title || ""} 
                    onChange={(e) => setNewSession({...newSession, title: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input 
                    placeholder="e.g., Gym Floor A, Studio B" 
                    value={newSession.location || ""} 
                    onChange={(e) => setNewSession({...newSession, location: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea 
                    placeholder="Session description or special instructions" 
                    rows={3} 
                    value={newSession.description || ""} 
                    onChange={(e) => setNewSession({...newSession, description: e.target.value})}
                  />
                </div>

                <div className="flex gap-2 pt-4">
                  <Button
                    variant="outline"
                    className="flex-1 bg-transparent"
                    onClick={() => setShowBookingModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button className="flex-1" onClick={handleCreateSession}>
                    Book Session
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Calendar Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={() => navigateWeek("prev")}>
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => navigateWeek("next")}>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
              <h2 className="text-xl font-semibold">
                {weekDates[0].toLocaleDateString("en-US", { month: "long", year: "numeric" })}
              </h2>
              <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date())}>
                Today
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant={viewMode === "day" ? "default" : "outline"} size="sm" onClick={() => setViewMode("day")}>
                Day
              </Button>
              <Button
                variant={viewMode === "week" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("week")}
              >
                Week
              </Button>
              <Button
                variant={viewMode === "month" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("month")}
              >
                Month
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Week View Calendar */}
      {viewMode === "week" && (
        <Card className="animate-in slide-in-from-bottom-4 duration-500">
          <CardContent className="p-0">
            <div className="grid grid-cols-8 border-b">
              {/* Time column header */}
              <div className="p-4 border-r bg-muted/30">
                <span className="text-sm font-medium text-muted-foreground">Time</span>
              </div>
              {/* Day headers */}
              {weekDates.map((date, index) => (
                <div key={index} className="p-4 text-center border-r last:border-r-0">
                  <div className="text-sm font-medium text-muted-foreground">{weekDays[index]}</div>
                  <div
                    className={`text-lg font-semibold ${
                      date.toDateString() === new Date().toDateString() ? "text-primary" : "text-foreground"
                    }`}
                  >
                    {date.getDate()}
                  </div>
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="relative">
              {timeSlots.map((time, timeIndex) => (
                <div key={time} className="grid grid-cols-8 border-b last:border-b-0 min-h-[60px]">
                  {/* Time label */}
                  <div className="p-2 border-r bg-muted/10 flex items-start">
                    <span className="text-xs text-muted-foreground">{time}</span>
                  </div>
                  {/* Day columns */}
                  {weekDates.map((date, dayIndex) => (
                    <div
                      key={dayIndex}
                      className="border-r last:border-r-0 relative cursor-pointer hover:bg-muted/20 transition-colors"
                      onClick={() => handleTimeSlotClick(date, time)}
                    >
                      {/* Sessions for this time slot */}
                      {getSessionsForDate(date)
                        .filter((session) => {
                          const sessionStartHour = new Date(session.scheduled_start).getHours()
                          const slotHour = Number.parseInt(time.split(":")[0])
                          return sessionStartHour === slotHour
                        })
                        .map((session) => {
                          const position = getSessionPosition(session.scheduled_start, session.duration_minutes || 60)
                          const sessionTypeColor = getSessionTypeColor(session.session_type)
                          return (
                            <div
                              key={session.id}
                              className={`absolute left-1 right-1 ${sessionTypeColor} text-white text-xs p-1 rounded cursor-pointer hover:opacity-90 transition-opacity animate-in slide-in-from-top-2`}
                              style={{
                                top: `${position.top - timeIndex * 60}px`,
                                height: `${position.height}px`,
                                zIndex: 10,
                              }}
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedSession(session)
                              }}
                            >
                              <div className="font-medium truncate">
                                {session.client_name || 'Unknown Client'}
                              </div>
                              <div className="truncate opacity-90">
                                {session.session_type.replace('_', ' ')}
                              </div>
                              <div className="truncate text-xs opacity-75">
                                {formatTime(session.scheduled_start)}
                              </div>
                            </div>
                          )
                        })}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Today's Sessions Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {/* Upcoming Sessions */}
          <Card className="animate-in slide-in-from-left-4 duration-500">
            <CardHeader>
              <CardTitle>Today's Sessions</CardTitle>
              <CardDescription>Your scheduled sessions for today</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {todaySessions.length > 0 ? (
                  todaySessions.map((session, index) => (
                    <div
                      key={session.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer animate-in slide-in-from-bottom-2"
                      style={{ animationDelay: `${index * 100}ms` }}
                      onClick={() => setSelectedSession(session)}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-3 h-3 rounded-full ${getSessionTypeColor(session.session_type)}`} />
                        <div>
                          <p className="font-medium">{session.client_name || 'Unknown Client'}</p>
                          <p className="text-sm text-muted-foreground">
                            {session.session_type.replace('_', ' ')}
                          </p>
                          {session.location && (
                            <p className="text-xs text-muted-foreground">{session.location}</p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">
                          {formatTime(session.scheduled_start)} - {formatTime(session.scheduled_end)}
                        </p>
                        <Badge className={getStatusColor(session.status)}>
                          {session.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-8">No sessions scheduled for today</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          {/* Quick Stats */}
          <Card className="animate-in slide-in-from-right-4 duration-500">
            <CardHeader>
              <CardTitle>Today's Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-primary" />
                  <span className="text-sm">Total Sessions</span>
                </div>
                <span className="font-medium">{todayStats.totalSessions}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-primary" />
                  <span className="text-sm">Total Hours</span>
                </div>
                <span className="font-medium">{todayStats.totalHours.toFixed(1)}h</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-primary" />
                  <span className="text-sm">Clients</span>
                </div>
                <span className="font-medium">{todayStats.uniqueClients}</span>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="animate-in slide-in-from-right-4 duration-700">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button 
                variant="outline" 
                className="w-full justify-start bg-transparent"
                onClick={() => setShowBookingModal(true)}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Session
              </Button>
              <Button variant="outline" className="w-full justify-start bg-transparent">
                <Calendar className="w-4 h-4 mr-2" />
                Block Time Off
              </Button>
              <Button variant="outline" className="w-full justify-start bg-transparent">
                <Users className="w-4 h-4 mr-2" />
                Recurring Sessions
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Session Detail Modal */}
      {selectedSession && (
        <Dialog open={!!selectedSession} onOpenChange={() => setSelectedSession(null)}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Session Details</DialogTitle>
              <DialogDescription>
                {formatDate(selectedSession.scheduled_start)} • {formatTime(selectedSession.scheduled_start)} - {formatTime(selectedSession.scheduled_end)}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div>
                  <h3 className="font-medium">{selectedSession.client_name || 'Unknown Client'}</h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedSession.session_type.replace('_', ' ')}
                  </p>
                  {selectedSession.title && (
                    <p className="text-sm text-muted-foreground">{selectedSession.title}</p>
                  )}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Duration</span>
                  <span className="font-medium">{selectedSession.duration_minutes || 60} minutes</span>
                </div>
                {selectedSession.location && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Location</span>
                    <span className="font-medium">{selectedSession.location}</span>
                  </div>
                )}
                {selectedSession.room_number && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Room</span>
                    <span className="font-medium">{selectedSession.room_number}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <Badge className={getStatusColor(selectedSession.status)}>
                    {selectedSession.status.replace('_', ' ')}
                  </Badge>
                </div>
                {selectedSession.price && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Price</span>
                    <span className="font-medium">${selectedSession.price}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Payment Status</span>
                  <Badge className={selectedSession.is_paid ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                    {selectedSession.is_paid ? "Paid" : "Unpaid"}
                  </Badge>
                </div>
              </div>

              {selectedSession.description && (
                <div>
                  <span className="text-sm text-muted-foreground">Description</span>
                  <p className="text-sm mt-1 p-2 bg-muted/50 rounded">{selectedSession.description}</p>
                </div>
              )}

              {selectedSession.planned_activities && selectedSession.planned_activities.length > 0 && (
                <div>
                  <span className="text-sm text-muted-foreground">Planned Activities</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedSession.planned_activities.map((activity, index) => (
                      <Badge key={index} variant="outline" className="text-xs">{activity}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {selectedSession.trainer_notes_before && (
                <div>
                  <span className="text-sm text-muted-foreground">Trainer Notes (Before)</span>
                  <p className="text-sm mt-1 p-2 bg-muted/50 rounded">{selectedSession.trainer_notes_before}</p>
                </div>
              )}

              {selectedSession.client_notes && (
                <div>
                  <span className="text-sm text-muted-foreground">Client Notes</span>
                  <p className="text-sm mt-1 p-2 bg-muted/50 rounded">{selectedSession.client_notes}</p>
                </div>
              )}

              <div className="flex gap-2 pt-4">
                {selectedSession.status === "pending" && (
                  <Button 
                    variant="outline" 
                    className="flex-1 bg-transparent"
                    onClick={() => handleConfirmSession(selectedSession.id)}
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Confirm
                  </Button>
                )}
                
                {selectedSession.status !== "cancelled" && selectedSession.status !== "completed" && (
                  <Button 
                    variant="outline" 
                    className="flex-1 bg-transparent"
                    onClick={() => handleCancelSession(selectedSession.id)}
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

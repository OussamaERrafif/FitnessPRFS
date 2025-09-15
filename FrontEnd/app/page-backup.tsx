"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Users, Calendar, DollarSign, TrendingUp, Clock, CheckCircle, ArrowRight, Plus } from "lucide-react"

// Mock data
const overviewStats = [
  {
    title: "Total Clients",
    value: "127",
    change: "+12%",
    trend: "up",
    icon: Users,
    color: "text-blue-600",
  },
  {
    title: "Active Plans",
    value: "89",
    change: "+8%",
    trend: "up",
    icon: CheckCircle,
    color: "text-green-600",
  },
  {
    title: "This Week Sessions",
    value: "34",
    change: "+5%",
    trend: "up",
    icon: Calendar,
    color: "text-purple-600",
  },
  {
    title: "Monthly Revenue",
    value: "$12,450",
    change: "+15%",
    trend: "up",
    icon: DollarSign,
    color: "text-emerald-600",
  },
]

const recentClients = [
  {
    id: 1,
    name: "Sarah Johnson",
    avatar: "/fit-woman-outdoors.png",
    status: "active",
    lastActivity: "2 hours ago",
    progress: 85,
    goal: "Weight Loss",
  },
  {
    id: 2,
    name: "Mike Chen",
    avatar: "/fit-man-gym.png",
    status: "needs-attention",
    lastActivity: "1 day ago",
    progress: 45,
    goal: "Muscle Gain",
  },
  {
    id: 3,
    name: "Emma Davis",
    avatar: "/woman-athlete.jpg",
    status: "active",
    lastActivity: "3 hours ago",
    progress: 92,
    goal: "Endurance",
  },
  {
    id: 4,
    name: "Alex Rodriguez",
    avatar: "/man-athlete.png",
    status: "active",
    lastActivity: "5 hours ago",
    progress: 78,
    goal: "Strength",
  },
]

const upcomingSessions = [
  {
    id: 1,
    client: "Sarah Johnson",
    time: "9:00 AM",
    type: "Personal Training",
    status: "confirmed",
  },
  {
    id: 2,
    client: "Mike Chen",
    time: "11:00 AM",
    type: "Nutrition Consultation",
    status: "pending",
  },
  {
    id: 3,
    client: "Emma Davis",
    time: "2:00 PM",
    type: "Group Session",
    status: "confirmed",
  },
]

export default function Dashboard() {
  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back, John! Here's your training overview.</p>
        </div>
        <Button className="bg-primary hover:bg-primary/90">
          <Plus className="w-4 h-4 mr-2" />
          Quick Actions
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {overviewStats.map((stat, index) => (
          <Card
            key={stat.title}
            className="hover:shadow-md transition-all duration-200 animate-in slide-in-from-bottom-4"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <TrendingUp className="w-3 h-3 mr-1 text-green-600" />
                <span className="text-green-600">{stat.change}</span>
                <span className="ml-1">from last month</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Client Progress Feed */}
        <div className="lg:col-span-2">
          <Card className="animate-in slide-in-from-left-4 duration-500">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Client Progress</CardTitle>
                  <CardDescription>Recent activity and progress updates</CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  View All
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentClients.map((client, index) => (
                <div
                  key={client.id}
                  className="flex items-center space-x-4 p-3 rounded-lg hover:bg-muted/50 transition-colors duration-200 animate-in slide-in-from-bottom-2"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <Avatar className="w-10 h-10">
                    <AvatarImage src={client.avatar || "/placeholder.svg"} />
                    <AvatarFallback>
                      {client.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-foreground truncate">{client.name}</p>
                      <Badge variant={client.status === "active" ? "default" : "secondary"} className="ml-2">
                        {client.status === "active" ? "Active" : "Needs Attention"}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs text-muted-foreground">
                        {client.goal} • {client.lastActivity}
                      </p>
                      <span className="text-xs text-muted-foreground">{client.progress}%</span>
                    </div>
                    <Progress value={client.progress} className="mt-2 h-2" />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Content */}
        <div className="space-y-6">
          {/* Today's Schedule */}
          <Card className="animate-in slide-in-from-right-4 duration-500">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="w-5 h-5 mr-2 text-primary" />
                Today's Schedule
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {upcomingSessions.map((session, index) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/30 animate-in slide-in-from-bottom-2"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">{session.client}</p>
                    <p className="text-xs text-muted-foreground">{session.type}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-foreground">{session.time}</p>
                    <Badge variant={session.status === "confirmed" ? "default" : "secondary"} className="text-xs">
                      {session.status}
                    </Badge>
                  </div>
                </div>
              ))}
              <Button variant="outline" className="w-full mt-4 bg-transparent">
                <Calendar className="w-4 h-4 mr-2" />
                View Full Calendar
              </Button>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="animate-in slide-in-from-right-4 duration-700">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start bg-transparent">
                <Users className="w-4 h-4 mr-2" />
                Add New Client
              </Button>
              <Button variant="outline" className="w-full justify-start bg-transparent">
                <Calendar className="w-4 h-4 mr-2" />
                Schedule Session
              </Button>
              <Button variant="outline" className="w-full justify-start bg-transparent">
                <CheckCircle className="w-4 h-4 mr-2" />
                Create Training Plan
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

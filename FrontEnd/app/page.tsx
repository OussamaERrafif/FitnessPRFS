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
    plan: "Strength Training",
    progress: 85,
    goal: "Weight Loss",
  },
  {
    id: 2,
    name: "Mike Chen",
    avatar: "/man-athlete.png",
    plan: "Cardio Intensive",
    progress: 92,
    goal: "Endurance",
  },
  {
    id: 3,
    name: "Emma Davis",
    avatar: "/fitness-woman.png",
    plan: "Yoga & Flexibility",
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

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {overviewStats.map((stat, index) => {
          const IconComponent = stat.icon
          return (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <IconComponent className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1 text-green-500" />
                  {stat.change} from last month
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Clients */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="w-5 h-5 mr-2" />
              Recent Client Progress
            </CardTitle>
            <CardDescription>
              Track your clients' latest achievements and goals
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentClients.map((client) => (
              <div key={client.id} className="flex items-center space-x-4 p-3 rounded-lg border bg-card">
                <Avatar className="w-12 h-12">
                  <AvatarImage src={client.avatar} alt={client.name} />
                  <AvatarFallback>{client.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{client.name}</p>
                  <p className="text-sm text-muted-foreground">{client.plan}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Progress value={client.progress} className="flex-1 h-2" />
                    <span className="text-xs font-medium">{client.progress}%</span>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant="outline" className="text-xs">
                    {client.goal}
                  </Badge>
                </div>
              </div>
            ))}
            <Button variant="outline" className="w-full">
              <ArrowRight className="w-4 h-4 mr-2" />
              View All Clients
            </Button>
          </CardContent>
        </Card>

        {/* Upcoming Sessions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Today's Sessions
            </CardTitle>
            <CardDescription>
              Your scheduled appointments
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {upcomingSessions.map((session) => (
              <div key={session.id} className="flex items-center justify-between p-3 rounded-lg border bg-card">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10">
                    <Clock className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-sm">{session.client}</p>
                    <p className="text-xs text-muted-foreground">{session.type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium">{session.time}</p>
                  <Badge 
                    variant={session.status === 'confirmed' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {session.status}
                  </Badge>
                </div>
              </div>
            ))}
            <Button variant="outline" className="w-full">
              <ArrowRight className="w-4 h-4 mr-2" />
              View Schedule
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start bg-transparent">
              <Plus className="w-4 h-4 mr-2" />
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
  )
}

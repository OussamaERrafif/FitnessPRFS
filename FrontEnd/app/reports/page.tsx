"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { Download, TrendingUp, TrendingDown, Users, DollarSign, Calendar, Target, FileText, Filter } from "lucide-react"

// Mock data for analytics
const revenueData = [
  { month: "Jan", revenue: 8500, clients: 45, sessions: 180 },
  { month: "Feb", revenue: 9200, clients: 48, sessions: 195 },
  { month: "Mar", revenue: 10100, clients: 52, sessions: 210 },
  { month: "Apr", revenue: 11300, clients: 58, sessions: 235 },
  { month: "May", revenue: 12450, clients: 62, sessions: 248 },
  { month: "Jun", revenue: 13200, clients: 65, sessions: 260 },
]

const clientProgressData = [
  { week: "Week 1", completed: 95, dropped: 5 },
  { week: "Week 2", completed: 92, dropped: 8 },
  { week: "Week 3", completed: 89, dropped: 11 },
  { week: "Week 4", completed: 87, dropped: 13 },
  { week: "Week 5", completed: 85, dropped: 15 },
  { week: "Week 6", completed: 83, dropped: 17 },
  { week: "Week 7", completed: 81, dropped: 19 },
  { week: "Week 8", completed: 79, dropped: 21 },
]

const sessionTypeData = [
  { name: "Personal Training", value: 65, color: "#0891b2" },
  { name: "Group Sessions", value: 20, color: "#6366f1" },
  { name: "Consultations", value: 10, color: "#f59e0b" },
  { name: "Assessments", value: 5, color: "#ef4444" },
]

const clientRetentionData = [
  { period: "0-1 months", retained: 95, churned: 5 },
  { period: "1-3 months", retained: 87, churned: 13 },
  { period: "3-6 months", retained: 78, churned: 22 },
  { period: "6-12 months", retained: 72, churned: 28 },
  { period: "12+ months", retained: 68, churned: 32 },
]

const topPerformingPlans = [
  {
    name: "Beginner Weight Loss",
    clients: 15,
    completionRate: 89,
    avgRating: 4.7,
    revenue: 2985,
  },
  {
    name: "Advanced Strength Building",
    clients: 8,
    completionRate: 94,
    avgRating: 4.9,
    revenue: 2240,
  },
  {
    name: "HIIT Endurance Boost",
    clients: 22,
    completionRate: 87,
    avgRating: 4.6,
    revenue: 3960,
  },
  {
    name: "Functional Fitness",
    clients: 12,
    completionRate: 91,
    avgRating: 4.8,
    revenue: 2160,
  },
]

export default function ReportsPage() {
  const [dateRange, setDateRange] = useState("6months")
  const [activeTab, setActiveTab] = useState("overview")

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value)
  }

  const calculateGrowth = (current: number, previous: number) => {
    return ((current - previous) / previous) * 100
  }

  const currentRevenue = revenueData[revenueData.length - 1].revenue
  const previousRevenue = revenueData[revenueData.length - 2].revenue
  const revenueGrowth = calculateGrowth(currentRevenue, previousRevenue)

  const currentClients = revenueData[revenueData.length - 1].clients
  const previousClients = revenueData[revenueData.length - 2].clients
  const clientGrowth = calculateGrowth(currentClients, previousClients)

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Reports & Analytics</h1>
          <p className="text-muted-foreground">Track your business performance and client success</p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1month">Last Month</SelectItem>
              <SelectItem value="3months">Last 3 Months</SelectItem>
              <SelectItem value="6months">Last 6 Months</SelectItem>
              <SelectItem value="1year">Last Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button className="bg-primary hover:bg-primary/90">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="animate-in slide-in-from-bottom-4 duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <DollarSign className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(currentRevenue)}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              {revenueGrowth > 0 ? (
                <TrendingUp className="w-3 h-3 mr-1 text-green-600" />
              ) : (
                <TrendingDown className="w-3 h-3 mr-1 text-red-600" />
              )}
              <span className={revenueGrowth > 0 ? "text-green-600" : "text-red-600"}>
                {Math.abs(revenueGrowth).toFixed(1)}%
              </span>
              <span className="ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-in slide-in-from-bottom-4 duration-400">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Clients</CardTitle>
            <Users className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentClients}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              {clientGrowth > 0 ? (
                <TrendingUp className="w-3 h-3 mr-1 text-green-600" />
              ) : (
                <TrendingDown className="w-3 h-3 mr-1 text-red-600" />
              )}
              <span className={clientGrowth > 0 ? "text-green-600" : "text-red-600"}>
                {Math.abs(clientGrowth).toFixed(1)}%
              </span>
              <span className="ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-in slide-in-from-bottom-4 duration-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sessions This Month</CardTitle>
            <Calendar className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{revenueData[revenueData.length - 1].sessions}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="w-3 h-3 mr-1 text-green-600" />
              <span className="text-green-600">4.8%</span>
              <span className="ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-in slide-in-from-bottom-4 duration-600">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Success Rate</CardTitle>
            <Target className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87%</div>
            <div className="flex items-center text-xs text-muted-foreground">
              <TrendingUp className="w-3 h-3 mr-1 text-green-600" />
              <span className="text-green-600">2.1%</span>
              <span className="ml-1">from last month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabbed Analytics */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Business Overview</TabsTrigger>
          <TabsTrigger value="clients">Client Analytics</TabsTrigger>
          <TabsTrigger value="programs">Program Performance</TabsTrigger>
          <TabsTrigger value="financial">Financial Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Trend */}
            <Card className="animate-in slide-in-from-left-4 duration-500">
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
                <CardDescription>Monthly revenue growth over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={revenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Area type="monotone" dataKey="revenue" stroke="#0891b2" fill="#0891b2" fillOpacity={0.2} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Session Types Distribution */}
            <Card className="animate-in slide-in-from-right-4 duration-500">
              <CardHeader>
                <CardTitle>Session Types</CardTitle>
                <CardDescription>Distribution of session types</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sessionTypeData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {sessionTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Client Growth */}
          <Card className="animate-in slide-in-from-bottom-4 duration-700">
            <CardHeader>
              <CardTitle>Client Growth</CardTitle>
              <CardDescription>Monthly client acquisition and session volume</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="clients" fill="#0891b2" name="Clients" />
                  <Bar yAxisId="right" dataKey="sessions" fill="#6366f1" name="Sessions" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="clients" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Client Progress Tracking */}
            <Card className="animate-in slide-in-from-left-4 duration-500">
              <CardHeader>
                <CardTitle>Client Progress Tracking</CardTitle>
                <CardDescription>Weekly completion vs dropout rates</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={clientProgressData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="week" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="completed"
                      stackId="1"
                      stroke="#10b981"
                      fill="#10b981"
                      name="Completed"
                    />
                    <Area
                      type="monotone"
                      dataKey="dropped"
                      stackId="1"
                      stroke="#ef4444"
                      fill="#ef4444"
                      name="Dropped"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Client Retention */}
            <Card className="animate-in slide-in-from-right-4 duration-500">
              <CardHeader>
                <CardTitle>Client Retention</CardTitle>
                <CardDescription>Retention rates by time period</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={clientRetentionData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="period" type="category" width={80} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="retained" fill="#10b981" name="Retained %" />
                    <Bar dataKey="churned" fill="#ef4444" name="Churned %" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Client Success Metrics */}
          <Card className="animate-in slide-in-from-bottom-4 duration-700">
            <CardHeader>
              <CardTitle>Client Success Metrics</CardTitle>
              <CardDescription>Key performance indicators for client outcomes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-muted/30 rounded-lg">
                  <div className="text-3xl font-bold text-primary">87%</div>
                  <p className="text-sm text-muted-foreground">Average Goal Achievement</p>
                </div>
                <div className="text-center p-6 bg-muted/30 rounded-lg">
                  <div className="text-3xl font-bold text-primary">92%</div>
                  <p className="text-sm text-muted-foreground">Session Attendance Rate</p>
                </div>
                <div className="text-center p-6 bg-muted/30 rounded-lg">
                  <div className="text-3xl font-bold text-primary">4.7</div>
                  <p className="text-sm text-muted-foreground">Average Client Rating</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="programs" className="space-y-6">
          {/* Top Performing Plans */}
          <Card className="animate-in slide-in-from-bottom-4 duration-500">
            <CardHeader>
              <CardTitle>Top Performing Training Plans</CardTitle>
              <CardDescription>Plans ranked by success rate and client satisfaction</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topPerformingPlans.map((plan, index) => (
                  <div
                    key={plan.name}
                    className="flex items-center justify-between p-4 border rounded-lg animate-in slide-in-from-bottom-2"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="flex-1">
                      <h4 className="font-medium">{plan.name}</h4>
                      <p className="text-sm text-muted-foreground">{plan.clients} active clients</p>
                    </div>
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="text-center">
                        <p className="font-medium text-primary">{plan.completionRate}%</p>
                        <p className="text-xs text-muted-foreground">Completion</p>
                      </div>
                      <div className="text-center">
                        <p className="font-medium text-primary">{plan.avgRating}</p>
                        <p className="text-xs text-muted-foreground">Rating</p>
                      </div>
                      <div className="text-center">
                        <p className="font-medium text-primary">{formatCurrency(plan.revenue)}</p>
                        <p className="text-xs text-muted-foreground">Revenue</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Program Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="animate-in slide-in-from-left-4 duration-700">
              <CardHeader>
                <CardTitle>Program Completion Rates</CardTitle>
                <CardDescription>Success rates by program type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Weight Loss Programs</span>
                      <span>89%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: "89%" }} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Strength Building</span>
                      <span>94%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: "94%" }} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Endurance Training</span>
                      <span>87%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: "87%" }} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>General Fitness</span>
                      <span>91%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div className="bg-primary h-2 rounded-full" style={{ width: "91%" }} />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="animate-in slide-in-from-right-4 duration-700">
              <CardHeader>
                <CardTitle>Program Popularity</CardTitle>
                <CardDescription>Most requested program types</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={topPerformingPlans}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="clients" fill="#0891b2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="financial" className="space-y-6">
          {/* Revenue Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="animate-in slide-in-from-left-4 duration-500">
              <CardHeader>
                <CardTitle>Revenue by Service Type</CardTitle>
                <CardDescription>Income breakdown by service category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full" />
                      <span className="text-sm">Personal Training</span>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(8100)}</p>
                      <p className="text-xs text-muted-foreground">65%</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full" />
                      <span className="text-sm">Group Sessions</span>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(2490)}</p>
                      <p className="text-xs text-muted-foreground">20%</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                      <span className="text-sm">Consultations</span>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(1245)}</p>
                      <p className="text-xs text-muted-foreground">10%</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full" />
                      <span className="text-sm">Assessments</span>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(615)}</p>
                      <p className="text-xs text-muted-foreground">5%</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="animate-in slide-in-from-right-4 duration-500">
              <CardHeader>
                <CardTitle>Monthly Financial Summary</CardTitle>
                <CardDescription>Key financial metrics for this month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Gross Revenue</span>
                    <span className="font-medium">{formatCurrency(13200)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Platform Fees</span>
                    <span className="font-medium text-red-600">-{formatCurrency(396)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Equipment Costs</span>
                    <span className="font-medium text-red-600">-{formatCurrency(200)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Marketing</span>
                    <span className="font-medium text-red-600">-{formatCurrency(150)}</span>
                  </div>
                  <div className="border-t pt-2">
                    <div className="flex justify-between font-medium">
                      <span>Net Revenue</span>
                      <span className="text-green-600">{formatCurrency(12454)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Export Options */}
          <Card className="animate-in slide-in-from-bottom-4 duration-700">
            <CardHeader>
              <CardTitle>Export Reports</CardTitle>
              <CardDescription>Download detailed reports for accounting and analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button variant="outline" className="h-20 flex-col bg-transparent">
                  <FileText className="w-6 h-6 mb-2" />
                  <span>Revenue Report</span>
                  <span className="text-xs text-muted-foreground">PDF/Excel</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col bg-transparent">
                  <Users className="w-6 h-6 mb-2" />
                  <span>Client Report</span>
                  <span className="text-xs text-muted-foreground">PDF/Excel</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col bg-transparent">
                  <Target className="w-6 h-6 mb-2" />
                  <span>Performance Report</span>
                  <span className="text-xs text-muted-foreground">PDF/Excel</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

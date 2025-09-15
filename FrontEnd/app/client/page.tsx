"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  Target,
  TrendingUp,
  Dumbbell,
  Apple,
  Clock,
  Award,
  ChevronRight,
  Lock,
  Activity,
  Heart,
  Scale,
} from "lucide-react"

// Mock client data
const mockClientData = {
  id: 1,
  name: "Sarah Johnson",
  email: "sarah.johnson@email.com",
  avatar: "/fit-woman-outdoors.png",
  pin: "1234",
  joinDate: "2024-01-15",
  currentWeight: 68,
  targetWeight: 65,
  startWeight: 75,
  height: 165,
  age: 28,
  goals: ["Weight Loss", "Muscle Tone", "Endurance"],
  trainer: "Mike Wilson",
  nextSession: "2024-12-10T10:00:00",
  weeklyProgress: {
    workouts: 4,
    targetWorkouts: 5,
    meals: 18,
    targetMeals: 21,
    water: 85,
    sleep: 7.2,
  },
  recentWorkouts: [
    { date: "2024-12-09", name: "Upper Body Strength", duration: 45, completed: true },
    { date: "2024-12-07", name: "HIIT Cardio", duration: 30, completed: true },
    { date: "2024-12-05", name: "Lower Body Power", duration: 50, completed: true },
    { date: "2024-12-03", name: "Core & Flexibility", duration: 35, completed: false },
  ],
  currentProgram: {
    name: "12-Week Transformation",
    week: 8,
    totalWeeks: 12,
    progress: 67,
  },
  todaysMeals: [
    { time: "Breakfast", name: "Protein Oatmeal Bowl", calories: 320, completed: true },
    { time: "Lunch", name: "Grilled Chicken Salad", calories: 450, completed: true },
    { time: "Snack", name: "Greek Yogurt & Berries", calories: 180, completed: false },
    { time: "Dinner", name: "Salmon with Quinoa", calories: 520, completed: false },
  ],
  achievements: [
    { name: "First Week Complete", date: "2024-01-22", icon: "🎯" },
    { name: "5kg Lost", date: "2024-03-15", icon: "⚖️" },
    { name: "Consistency Champion", date: "2024-11-01", icon: "🏆" },
  ],
}

export default function ClientDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [pin, setPin] = useState("")
  const [error, setError] = useState("")

  const handlePinSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (pin === "1234") {
      setIsAuthenticated(true)
      setError("")
    } else {
      setError("Invalid PIN. Please try again.")
      setPin("")
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center">
              <Lock className="w-8 h-8 text-emerald-600" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold">Client Portal</CardTitle>
              <CardDescription>Enter your PIN to access your dashboard</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePinSubmit} className="space-y-4">
              <div>
                <Input
                  type="password"
                  placeholder="Enter your PIN"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  className="text-center text-lg tracking-widest"
                  maxLength={4}
                />
                {error && <p className="text-sm text-red-500 mt-2">{error}</p>}
              </div>
              <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700">
                Access Dashboard
              </Button>
              <p className="text-xs text-center text-muted-foreground">Demo PIN: 1234</p>
            </form>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      {/* Header */}
      <header className="bg-white border-b border-emerald-100 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Avatar className="w-12 h-12">
              <AvatarImage src={mockClientData.avatar || "/placeholder.svg"} alt={mockClientData.name} />
              <AvatarFallback>
                {mockClientData.name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Welcome back, {mockClientData.name}!</h1>
              <p className="text-sm text-gray-600">Let's crush today's goals 💪</p>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => setIsAuthenticated(false)}
            className="border-emerald-200 text-emerald-700 hover:bg-emerald-50"
          >
            Sign Out
          </Button>
        </div>
      </header>

      <div className="p-6">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-white border border-emerald-100">
            <TabsTrigger
              value="overview"
              className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700"
            >
              <Activity className="w-4 h-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger
              value="training"
              className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700"
            >
              <Dumbbell className="w-4 h-4 mr-2" />
              Training
            </TabsTrigger>
            <TabsTrigger
              value="nutrition"
              className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700"
            >
              <Apple className="w-4 h-4 mr-2" />
              Nutrition
            </TabsTrigger>
            <TabsTrigger
              value="progress"
              className="data-[state=active]:bg-emerald-100 data-[state=active]:text-emerald-700"
            >
              <TrendingUp className="w-4 h-4 mr-2" />
              Progress
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-emerald-100 text-sm">Current Weight</p>
                      <p className="text-2xl font-bold">{mockClientData.currentWeight}kg</p>
                    </div>
                    <Scale className="w-8 h-8 text-emerald-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100 text-sm">Workouts This Week</p>
                      <p className="text-2xl font-bold">
                        {mockClientData.weeklyProgress.workouts}/{mockClientData.weeklyProgress.targetWorkouts}
                      </p>
                    </div>
                    <Dumbbell className="w-8 h-8 text-blue-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-orange-500 to-red-500 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-orange-100 text-sm">Meals Logged</p>
                      <p className="text-2xl font-bold">
                        {mockClientData.weeklyProgress.meals}/{mockClientData.weeklyProgress.targetMeals}
                      </p>
                    </div>
                    <Apple className="w-8 h-8 text-orange-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100 text-sm">Sleep Average</p>
                      <p className="text-2xl font-bold">{mockClientData.weeklyProgress.sleep}h</p>
                    </div>
                    <Heart className="w-8 h-8 text-purple-200" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Current Program Progress */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-emerald-600" />
                  Current Program
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{mockClientData.currentProgram.name}</h3>
                      <p className="text-sm text-gray-600">
                        Week {mockClientData.currentProgram.week} of {mockClientData.currentProgram.totalWeeks}
                      </p>
                    </div>
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">
                      {mockClientData.currentProgram.progress}% Complete
                    </Badge>
                  </div>
                  <Progress value={mockClientData.currentProgram.progress} className="h-3" />
                </div>
              </CardContent>
            </Card>

            {/* Today's Schedule */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-emerald-600" />
                    Today's Meals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {mockClientData.todaysMeals.map((meal, index) => (
                      <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-3 h-3 rounded-full ${meal.completed ? "bg-emerald-500" : "bg-gray-300"}`}
                          />
                          <div>
                            <p className="font-medium">{meal.name}</p>
                            <p className="text-sm text-gray-600">
                              {meal.time} • {meal.calories} cal
                            </p>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-emerald-600" />
                    Recent Achievements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {mockClientData.achievements.map((achievement, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 rounded-lg bg-emerald-50">
                        <span className="text-2xl">{achievement.icon}</span>
                        <div>
                          <p className="font-medium">{achievement.name}</p>
                          <p className="text-sm text-gray-600">{new Date(achievement.date).toLocaleDateString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="training" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Workouts</CardTitle>
                <CardDescription>Your training history and upcoming sessions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockClientData.recentWorkouts.map((workout, index) => (
                    <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-4 h-4 rounded-full ${workout.completed ? "bg-emerald-500" : "bg-gray-300"}`}
                        />
                        <div>
                          <h3 className="font-semibold">{workout.name}</h3>
                          <p className="text-sm text-gray-600">
                            {new Date(workout.date).toLocaleDateString()} • {workout.duration} min
                          </p>
                        </div>
                      </div>
                      <Badge variant={workout.completed ? "default" : "secondary"}>
                        {workout.completed ? "Completed" : "Missed"}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="nutrition" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Today's Nutrition Plan</CardTitle>
                <CardDescription>Track your meals and stay on target</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockClientData.todaysMeals.map((meal, index) => (
                    <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                      <div className="flex items-center gap-4">
                        <div className={`w-4 h-4 rounded-full ${meal.completed ? "bg-emerald-500" : "bg-gray-300"}`} />
                        <div>
                          <h3 className="font-semibold">{meal.name}</h3>
                          <p className="text-sm text-gray-600">
                            {meal.time} • {meal.calories} calories
                          </p>
                        </div>
                      </div>
                      <Button
                        variant={meal.completed ? "secondary" : "default"}
                        size="sm"
                        className={meal.completed ? "" : "bg-emerald-600 hover:bg-emerald-700"}
                      >
                        {meal.completed ? "Logged" : "Log Meal"}
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="progress" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Weight Progress</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span>Starting Weight</span>
                      <span className="font-semibold">{mockClientData.startWeight}kg</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Current Weight</span>
                      <span className="font-semibold">{mockClientData.currentWeight}kg</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Target Weight</span>
                      <span className="font-semibold">{mockClientData.targetWeight}kg</span>
                    </div>
                    <div className="pt-2">
                      <div className="flex justify-between text-sm mb-2">
                        <span>Progress to Goal</span>
                        <span className="font-semibold text-emerald-600">
                          {Math.round(
                            ((mockClientData.startWeight - mockClientData.currentWeight) /
                              (mockClientData.startWeight - mockClientData.targetWeight)) *
                              100,
                          )}
                          %
                        </span>
                      </div>
                      <Progress
                        value={
                          ((mockClientData.startWeight - mockClientData.currentWeight) /
                            (mockClientData.startWeight - mockClientData.targetWeight)) *
                          100
                        }
                        className="h-3"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Weekly Goals</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Workouts</span>
                        <span>
                          {mockClientData.weeklyProgress.workouts}/{mockClientData.weeklyProgress.targetWorkouts}
                        </span>
                      </div>
                      <Progress
                        value={
                          (mockClientData.weeklyProgress.workouts / mockClientData.weeklyProgress.targetWorkouts) * 100
                        }
                        className="h-2"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Meals Logged</span>
                        <span>
                          {mockClientData.weeklyProgress.meals}/{mockClientData.weeklyProgress.targetMeals}
                        </span>
                      </div>
                      <Progress
                        value={(mockClientData.weeklyProgress.meals / mockClientData.weeklyProgress.targetMeals) * 100}
                        className="h-2"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Water Intake</span>
                        <span>{mockClientData.weeklyProgress.water}%</span>
                      </div>
                      <Progress value={mockClientData.weeklyProgress.water} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

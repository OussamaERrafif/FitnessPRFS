"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, Plus, Trash2, GripVertical, Save, Eye, Download, Target } from "lucide-react"
import Link from "next/link"

// Mock exercise database
const exerciseDatabase = [
  {
    id: 1,
    name: "Push-ups",
    category: "Chest",
    equipment: "Bodyweight",
    difficulty: "Beginner",
    muscleGroups: ["Chest", "Shoulders", "Triceps"],
    instructions: "Start in plank position, lower body to ground, push back up",
  },
  {
    id: 2,
    name: "Squats",
    category: "Legs",
    equipment: "Bodyweight",
    difficulty: "Beginner",
    muscleGroups: ["Quadriceps", "Glutes", "Hamstrings"],
    instructions: "Stand with feet shoulder-width apart, lower into squat, return to standing",
  },
  {
    id: 3,
    name: "Bench Press",
    category: "Chest",
    equipment: "Barbell",
    difficulty: "Intermediate",
    muscleGroups: ["Chest", "Shoulders", "Triceps"],
    instructions: "Lie on bench, lower barbell to chest, press up to full extension",
  },
  {
    id: 4,
    name: "Deadlift",
    category: "Back",
    equipment: "Barbell",
    difficulty: "Advanced",
    muscleGroups: ["Back", "Glutes", "Hamstrings"],
    instructions: "Stand with feet hip-width apart, lift barbell from ground to hip level",
  },
  {
    id: 5,
    name: "Plank",
    category: "Core",
    equipment: "Bodyweight",
    difficulty: "Beginner",
    muscleGroups: ["Core", "Shoulders"],
    instructions: "Hold plank position with straight body line",
  },
]

interface Exercise {
  id: string
  exerciseId: number
  sets: number
  reps: string
  weight?: string
  rest: number
  notes?: string
}

interface WorkoutDay {
  id: string
  name: string
  exercises: Exercise[]
}

export default function PlanBuilder() {
  const [planName, setPlanName] = useState("")
  const [planDescription, setPlanDescription] = useState("")
  const [planGoal, setPlanGoal] = useState("")
  const [planDifficulty, setPlanDifficulty] = useState("")
  const [planDuration, setPlanDuration] = useState("")
  const [workoutDays, setWorkoutDays] = useState<WorkoutDay[]>([
    {
      id: "day-1",
      name: "Day 1 - Upper Body",
      exercises: [],
    },
  ])
  const [activeDay, setActiveDay] = useState("day-1")
  const [showExerciseDialog, setShowExerciseDialog] = useState(false)
  const [selectedMuscleGroup, setSelectedMuscleGroup] = useState("")

  const addWorkoutDay = () => {
    const newDay: WorkoutDay = {
      id: `day-${workoutDays.length + 1}`,
      name: `Day ${workoutDays.length + 1}`,
      exercises: [],
    }
    setWorkoutDays([...workoutDays, newDay])
    setActiveDay(newDay.id)
  }

  const removeWorkoutDay = (dayId: string) => {
    const updatedDays = workoutDays.filter((day) => day.id !== dayId)
    setWorkoutDays(updatedDays)
    if (activeDay === dayId && updatedDays.length > 0) {
      setActiveDay(updatedDays[0].id)
    }
  }

  const updateDayName = (dayId: string, newName: string) => {
    setWorkoutDays(workoutDays.map((day) => (day.id === dayId ? { ...day, name: newName } : day)))
  }

  const addExercise = (exerciseId: number) => {
    const newExercise: Exercise = {
      id: `exercise-${Date.now()}`,
      exerciseId,
      sets: 3,
      reps: "10-12",
      rest: 60,
    }

    setWorkoutDays(
      workoutDays.map((day) => (day.id === activeDay ? { ...day, exercises: [...day.exercises, newExercise] } : day)),
    )
    setShowExerciseDialog(false)
  }

  const removeExercise = (dayId: string, exerciseId: string) => {
    setWorkoutDays(
      workoutDays.map((day) =>
        day.id === dayId ? { ...day, exercises: day.exercises.filter((ex) => ex.id !== exerciseId) } : day,
      ),
    )
  }

  const updateExercise = (dayId: string, exerciseId: string, updates: Partial<Exercise>) => {
    setWorkoutDays(
      workoutDays.map((day) =>
        day.id === dayId
          ? {
              ...day,
              exercises: day.exercises.map((ex) => (ex.id === exerciseId ? { ...ex, ...updates } : ex)),
            }
          : day,
      ),
    )
  }

  const currentDay = workoutDays.find((day) => day.id === activeDay)
  const filteredExercises = selectedMuscleGroup
    ? exerciseDatabase.filter((ex) => ex.muscleGroups.includes(selectedMuscleGroup))
    : exerciseDatabase

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/training-plans">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Plans
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Plan Builder</h1>
            <p className="text-muted-foreground">Create a comprehensive training program</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Eye className="w-4 h-4 mr-2" />
            Preview
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button>
            <Save className="w-4 h-4 mr-2" />
            Save Plan
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Plan Details Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Plan Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="plan-name">Plan Name</Label>
                <Input
                  id="plan-name"
                  value={planName}
                  onChange={(e) => setPlanName(e.target.value)}
                  placeholder="Enter plan name"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="plan-description">Description</Label>
                <Textarea
                  id="plan-description"
                  value={planDescription}
                  onChange={(e) => setPlanDescription(e.target.value)}
                  placeholder="Describe the plan goals and approach"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="plan-goal">Primary Goal</Label>
                <Select value={planGoal} onValueChange={setPlanGoal}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select goal" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="weight-loss">Weight Loss</SelectItem>
                    <SelectItem value="muscle-gain">Muscle Gain</SelectItem>
                    <SelectItem value="strength">Strength</SelectItem>
                    <SelectItem value="endurance">Endurance</SelectItem>
                    <SelectItem value="general-fitness">General Fitness</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="plan-difficulty">Difficulty Level</Label>
                <Select value={planDifficulty} onValueChange={setPlanDifficulty}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select difficulty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="plan-duration">Duration</Label>
                <Select value={planDuration} onValueChange={setPlanDuration}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select duration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="4-weeks">4 Weeks</SelectItem>
                    <SelectItem value="8-weeks">8 Weeks</SelectItem>
                    <SelectItem value="12-weeks">12 Weeks</SelectItem>
                    <SelectItem value="16-weeks">16 Weeks</SelectItem>
                    <SelectItem value="custom">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Muscle Map */}
          <Card>
            <CardHeader>
              <CardTitle>Muscle Groups</CardTitle>
              <CardDescription>Click to filter exercises</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {["Chest", "Back", "Shoulders", "Arms", "Core", "Legs"].map((group) => (
                  <Button
                    key={group}
                    variant={selectedMuscleGroup === group ? "default" : "outline"}
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => setSelectedMuscleGroup(selectedMuscleGroup === group ? "" : group)}
                  >
                    <Target className="w-4 h-4 mr-2" />
                    {group}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Builder Area */}
        <div className="lg:col-span-3 space-y-6">
          {/* Workout Days Tabs */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Workout Days</CardTitle>
                <Button onClick={addWorkoutDay} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Day
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs value={activeDay} onValueChange={setActiveDay}>
                <TabsList className="grid w-full grid-cols-auto">
                  {workoutDays.map((day) => (
                    <TabsTrigger key={day.id} value={day.id} className="relative">
                      {day.name}
                      {workoutDays.length > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="absolute -top-2 -right-2 w-5 h-5 p-0 hover:bg-destructive hover:text-destructive-foreground"
                          onClick={(e) => {
                            e.stopPropagation()
                            removeWorkoutDay(day.id)
                          }}
                        >
                          ×
                        </Button>
                      )}
                    </TabsTrigger>
                  ))}
                </TabsList>

                {workoutDays.map((day) => (
                  <TabsContent key={day.id} value={day.id} className="space-y-4">
                    {/* Day Name Editor */}
                    <div className="flex items-center space-x-4">
                      <Input
                        value={day.name}
                        onChange={(e) => updateDayName(day.id, e.target.value)}
                        className="max-w-xs"
                      />
                      <Badge variant="outline">{day.exercises.length} exercises</Badge>
                    </div>

                    {/* Exercises List */}
                    <div className="space-y-3">
                      {day.exercises.map((exercise, index) => {
                        const exerciseData = exerciseDatabase.find((ex) => ex.id === exercise.exerciseId)
                        return (
                          <Card key={exercise.id} className="animate-in slide-in-from-bottom-2">
                            <CardContent className="p-4">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <GripVertical className="w-4 h-4 text-muted-foreground cursor-move" />
                                  <div>
                                    <h4 className="font-medium">{exerciseData?.name}</h4>
                                    <p className="text-sm text-muted-foreground">
                                      {exerciseData?.muscleGroups.join(", ")}
                                    </p>
                                  </div>
                                </div>
                                <Button variant="ghost" size="sm" onClick={() => removeExercise(day.id, exercise.id)}>
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>

                              <div className="grid grid-cols-4 gap-4 mt-4">
                                <div className="space-y-1">
                                  <Label className="text-xs">Sets</Label>
                                  <Input
                                    type="number"
                                    value={exercise.sets}
                                    onChange={(e) =>
                                      updateExercise(day.id, exercise.id, { sets: Number.parseInt(e.target.value) })
                                    }
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">Reps</Label>
                                  <Input
                                    value={exercise.reps}
                                    onChange={(e) => updateExercise(day.id, exercise.id, { reps: e.target.value })}
                                    placeholder="10-12"
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">Weight</Label>
                                  <Input
                                    value={exercise.weight || ""}
                                    onChange={(e) => updateExercise(day.id, exercise.id, { weight: e.target.value })}
                                    placeholder="BW"
                                    className="h-8"
                                  />
                                </div>
                                <div className="space-y-1">
                                  <Label className="text-xs">Rest (sec)</Label>
                                  <Input
                                    type="number"
                                    value={exercise.rest}
                                    onChange={(e) =>
                                      updateExercise(day.id, exercise.id, { rest: Number.parseInt(e.target.value) })
                                    }
                                    className="h-8"
                                  />
                                </div>
                              </div>

                              {exercise.notes && (
                                <div className="mt-3">
                                  <Label className="text-xs">Notes</Label>
                                  <Textarea
                                    value={exercise.notes}
                                    onChange={(e) => updateExercise(day.id, exercise.id, { notes: e.target.value })}
                                    placeholder="Exercise notes or modifications"
                                    rows={2}
                                    className="mt-1"
                                  />
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )
                      })}

                      {/* Add Exercise Button */}
                      <Dialog open={showExerciseDialog} onOpenChange={setShowExerciseDialog}>
                        <DialogTrigger asChild>
                          <Button variant="dashed" className="w-full h-16 border-2 border-dashed">
                            <Plus className="w-5 h-5 mr-2" />
                            Add Exercise
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Add Exercise</DialogTitle>
                            <DialogDescription>Choose an exercise to add to {currentDay?.name}</DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            {/* Exercise Search/Filter */}
                            <div className="flex gap-2">
                              <Input placeholder="Search exercises..." className="flex-1" />
                              <Select>
                                <SelectTrigger className="w-40">
                                  <SelectValue placeholder="Category" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="all">All Categories</SelectItem>
                                  <SelectItem value="chest">Chest</SelectItem>
                                  <SelectItem value="back">Back</SelectItem>
                                  <SelectItem value="legs">Legs</SelectItem>
                                  <SelectItem value="core">Core</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>

                            {/* Exercise List */}
                            <div className="max-h-96 overflow-auto space-y-2">
                              {filteredExercises.map((exercise) => (
                                <Card
                                  key={exercise.id}
                                  className="cursor-pointer hover:bg-muted/50 transition-colors"
                                  onClick={() => addExercise(exercise.id)}
                                >
                                  <CardContent className="p-3">
                                    <div className="flex items-center justify-between">
                                      <div>
                                        <h4 className="font-medium">{exercise.name}</h4>
                                        <p className="text-sm text-muted-foreground">
                                          {exercise.muscleGroups.join(", ")} • {exercise.equipment}
                                        </p>
                                      </div>
                                      <Badge variant="outline">{exercise.difficulty}</Badge>
                                    </div>
                                  </CardContent>
                                </Card>
                              ))}
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ArrowLeft, Plus, Save, Eye, Download, Calculator } from "lucide-react"
import Link from "next/link"

// Mock recipe database
const recipeDatabase = [
  {
    id: 1,
    name: "Grilled Chicken Salad",
    category: "Lunch",
    calories: 320,
    protein: 35,
    carbs: 12,
    fat: 14,
    cookTime: 15,
    difficulty: "Easy",
    tags: ["High Protein", "Low Carb"],
  },
  {
    id: 2,
    name: "Overnight Oats",
    category: "Breakfast",
    calories: 280,
    protein: 12,
    carbs: 45,
    fat: 8,
    cookTime: 5,
    difficulty: "Easy",
    tags: ["High Fiber", "Vegetarian"],
  },
  {
    id: 3,
    name: "Salmon with Quinoa",
    category: "Dinner",
    calories: 450,
    protein: 32,
    carbs: 35,
    fat: 22,
    cookTime: 25,
    difficulty: "Intermediate",
    tags: ["High Protein", "Omega-3"],
  },
  {
    id: 4,
    name: "Protein Smoothie Bowl",
    category: "Snack",
    calories: 220,
    protein: 25,
    carbs: 18,
    fat: 6,
    cookTime: 5,
    difficulty: "Easy",
    tags: ["High Protein", "Post Workout"],
  },
]

interface MealSlot {
  id: string
  recipeId?: number
  mealType: string
  day: string
}

interface WeekPlan {
  [key: string]: {
    breakfast?: MealSlot
    lunch?: MealSlot
    dinner?: MealSlot
    snack1?: MealSlot
    snack2?: MealSlot
  }
}

const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
const mealTypes = [
  { key: "breakfast", label: "Breakfast", color: "bg-orange-100 border-orange-200" },
  { key: "lunch", label: "Lunch", color: "bg-blue-100 border-blue-200" },
  { key: "dinner", label: "Dinner", color: "bg-purple-100 border-purple-200" },
  { key: "snack1", label: "Snack 1", color: "bg-green-100 border-green-200" },
  { key: "snack2", label: "Snack 2", color: "bg-yellow-100 border-yellow-200" },
]

export default function MealPlanBuilder() {
  const [planName, setPlanName] = useState("")
  const [planDescription, setPlanDescription] = useState("")
  const [planGoal, setPlanGoal] = useState("")
  const [planDifficulty, setPlanDifficulty] = useState("")
  const [targetCalories, setTargetCalories] = useState("")
  const [weekPlan, setWeekPlan] = useState<WeekPlan>({})
  const [showRecipeDialog, setShowRecipeDialog] = useState(false)
  const [selectedSlot, setSelectedSlot] = useState<{ day: string; mealType: string } | null>(null)
  const [selectedCategory, setSelectedCategory] = useState("")

  const addRecipeToSlot = (recipeId: number) => {
    if (!selectedSlot) return

    const slotId = `${selectedSlot.day}-${selectedSlot.mealType}`
    const newMeal: MealSlot = {
      id: slotId,
      recipeId,
      mealType: selectedSlot.mealType,
      day: selectedSlot.day,
    }

    setWeekPlan((prev) => ({
      ...prev,
      [selectedSlot.day]: {
        ...prev[selectedSlot.day],
        [selectedSlot.mealType]: newMeal,
      },
    }))
    setShowRecipeDialog(false)
    setSelectedSlot(null)
  }

  const removeRecipeFromSlot = (day: string, mealType: string) => {
    setWeekPlan((prev) => ({
      ...prev,
      [day]: {
        ...prev[day],
        [mealType]: undefined,
      },
    }))
  }

  const calculateDayTotals = (day: string) => {
    const dayMeals = weekPlan[day] || {}
    let totalCalories = 0
    let totalProtein = 0
    let totalCarbs = 0
    let totalFat = 0

    Object.values(dayMeals).forEach((meal) => {
      if (meal?.recipeId) {
        const recipe = recipeDatabase.find((r) => r.id === meal.recipeId)
        if (recipe) {
          totalCalories += recipe.calories
          totalProtein += recipe.protein
          totalCarbs += recipe.carbs
          totalFat += recipe.fat
        }
      }
    })

    return { totalCalories, totalProtein, totalCarbs, totalFat }
  }

  const calculateWeekAverages = () => {
    let totalCalories = 0
    let totalProtein = 0
    let totalCarbs = 0
    let totalFat = 0
    let daysWithMeals = 0

    daysOfWeek.forEach((day) => {
      const dayTotals = calculateDayTotals(day)
      if (dayTotals.totalCalories > 0) {
        totalCalories += dayTotals.totalCalories
        totalProtein += dayTotals.totalProtein
        totalCarbs += dayTotals.totalCarbs
        totalFat += dayTotals.totalFat
        daysWithMeals++
      }
    })

    if (daysWithMeals === 0) return { avgCalories: 0, avgProtein: 0, avgCarbs: 0, avgFat: 0 }

    return {
      avgCalories: Math.round(totalCalories / daysWithMeals),
      avgProtein: Math.round(totalProtein / daysWithMeals),
      avgCarbs: Math.round(totalCarbs / daysWithMeals),
      avgFat: Math.round(totalFat / daysWithMeals),
    }
  }

  const weekAverages = calculateWeekAverages()
  const filteredRecipes = selectedCategory
    ? recipeDatabase.filter((recipe) => recipe.category === selectedCategory)
    : recipeDatabase

  return (
    <div className="p-6 space-y-6 animate-in fade-in-50 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/meal-plans">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Plans
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Meal Plan Builder</h1>
            <p className="text-muted-foreground">Create a comprehensive nutrition program</p>
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
                  placeholder="Describe the nutrition plan"
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
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="endurance">Endurance</SelectItem>
                    <SelectItem value="general-health">General Health</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="target-calories">Target Calories/Day</Label>
                <Input
                  id="target-calories"
                  type="number"
                  value={targetCalories}
                  onChange={(e) => setTargetCalories(e.target.value)}
                  placeholder="e.g., 1800"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="plan-difficulty">Difficulty Level</Label>
                <Select value={planDifficulty} onValueChange={setPlanDifficulty}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select difficulty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="easy">Easy</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Nutrition Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calculator className="w-5 h-5 mr-2" />
                Nutrition Summary
              </CardTitle>
              <CardDescription>Daily averages</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">{weekAverages.avgCalories}</div>
                <p className="text-sm text-muted-foreground">Calories</p>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center p-2 bg-blue-50 rounded">
                  <p className="font-medium text-blue-700">{weekAverages.avgProtein}g</p>
                  <p className="text-blue-600">Protein</p>
                </div>
                <div className="text-center p-2 bg-green-50 rounded">
                  <p className="font-medium text-green-700">{weekAverages.avgCarbs}g</p>
                  <p className="text-green-600">Carbs</p>
                </div>
                <div className="text-center p-2 bg-yellow-50 rounded">
                  <p className="font-medium text-yellow-700">{weekAverages.avgFat}g</p>
                  <p className="text-yellow-600">Fat</p>
                </div>
              </div>
              {targetCalories && (
                <div className="text-center text-sm">
                  <p className="text-muted-foreground">Target: {targetCalories} calories</p>
                  <p
                    className={`font-medium ${
                      Math.abs(weekAverages.avgCalories - Number(targetCalories)) <= 50
                        ? "text-green-600"
                        : "text-orange-600"
                    }`}
                  >
                    {weekAverages.avgCalories > Number(targetCalories) ? "+" : ""}
                    {weekAverages.avgCalories - Number(targetCalories)} calories
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Main Builder Area */}
        <div className="lg:col-span-3 space-y-6">
          {/* Weekly Calendar */}
          <Card>
            <CardHeader>
              <CardTitle>Weekly Meal Plan</CardTitle>
              <CardDescription>Drag and drop recipes to build your meal plan</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Header Row */}
                <div className="grid grid-cols-6 gap-2">
                  <div className="font-medium text-sm text-muted-foreground">Meal</div>
                  {daysOfWeek.slice(0, 5).map((day) => (
                    <div key={day} className="font-medium text-sm text-center">
                      {day.slice(0, 3)}
                    </div>
                  ))}
                </div>

                {/* Meal Rows */}
                {mealTypes.map((mealType) => (
                  <div key={mealType.key} className="grid grid-cols-6 gap-2">
                    <div className="flex items-center">
                      <Badge variant="outline" className={mealType.color}>
                        {mealType.label}
                      </Badge>
                    </div>
                    {daysOfWeek.slice(0, 5).map((day) => {
                      const meal = weekPlan[day]?.[mealType.key as keyof (typeof weekPlan)[string]]
                      const recipe = meal?.recipeId ? recipeDatabase.find((r) => r.id === meal.recipeId) : null

                      return (
                        <div
                          key={`${day}-${mealType.key}`}
                          className="min-h-[80px] border-2 border-dashed border-muted rounded-lg p-2 cursor-pointer hover:border-primary/50 transition-colors"
                          onClick={() => {
                            setSelectedSlot({ day, mealType: mealType.key })
                            setShowRecipeDialog(true)
                          }}
                        >
                          {recipe ? (
                            <div className="relative group">
                              <div className="text-xs font-medium truncate">{recipe.name}</div>
                              <div className="text-xs text-muted-foreground">{recipe.calories} cal</div>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="absolute -top-1 -right-1 w-5 h-5 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  removeRecipeFromSlot(day, mealType.key)
                                }}
                              >
                                ×
                              </Button>
                            </div>
                          ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                              <Plus className="w-4 h-4" />
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                ))}

                {/* Daily Totals */}
                <div className="grid grid-cols-6 gap-2 pt-4 border-t">
                  <div className="font-medium text-sm">Daily Totals</div>
                  {daysOfWeek.slice(0, 5).map((day) => {
                    const totals = calculateDayTotals(day)
                    return (
                      <div key={day} className="text-center p-2 bg-muted/30 rounded">
                        <div className="text-sm font-medium">{totals.totalCalories}</div>
                        <div className="text-xs text-muted-foreground">calories</div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recipe Selection Dialog */}
      <Dialog open={showRecipeDialog} onOpenChange={setShowRecipeDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Recipe</DialogTitle>
            <DialogDescription>
              Choose a recipe for {selectedSlot?.mealType} on {selectedSlot?.day}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {/* Recipe Filter */}
            <div className="flex gap-2">
              <Input placeholder="Search recipes..." className="flex-1" />
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Categories</SelectItem>
                  <SelectItem value="Breakfast">Breakfast</SelectItem>
                  <SelectItem value="Lunch">Lunch</SelectItem>
                  <SelectItem value="Dinner">Dinner</SelectItem>
                  <SelectItem value="Snack">Snack</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Recipe List */}
            <div className="max-h-96 overflow-auto space-y-2">
              {filteredRecipes.map((recipe) => (
                <Card
                  key={recipe.id}
                  className="cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => addRecipeToSlot(recipe.id)}
                >
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{recipe.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {recipe.calories} cal • {recipe.protein}g protein • {recipe.cookTime} min
                        </p>
                        <div className="flex gap-1 mt-1">
                          {recipe.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <Badge variant="outline">{recipe.category}</Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

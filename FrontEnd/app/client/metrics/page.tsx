"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Save, TrendingUp, Scale, Ruler, Target, Calendar } from "lucide-react"
import Link from "next/link"

export default function ClientMetrics() {
  const [metrics, setMetrics] = useState({
    weight: "68",
    bodyFat: "22",
    muscleMass: "45",
    waist: "75",
    chest: "88",
    arms: "28",
    thighs: "55",
    notes: "",
  })

  const [goals, setGoals] = useState({
    targetWeight: "65",
    targetBodyFat: "18",
    targetDate: "2024-06-01",
    weeklyGoal: "Lose 0.5kg per week",
  })

  const handleMetricChange = (field: string, value: string) => {
    setMetrics((prev) => ({ ...prev, [field]: value }))
  }

  const handleGoalChange = (field: string, value: string) => {
    setGoals((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = () => {
    alert("Metrics updated successfully!")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/client">
            <Button
              variant="outline"
              size="sm"
              className="border-emerald-200 text-emerald-700 hover:bg-emerald-50 bg-transparent"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Update Metrics</h1>
            <p className="text-gray-600">Track your progress and update your goals</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Body Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="w-5 h-5 text-emerald-600" />
                Body Metrics
              </CardTitle>
              <CardDescription>Update your current measurements</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="weight">Weight (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    value={metrics.weight}
                    onChange={(e) => handleMetricChange("weight", e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="bodyFat">Body Fat (%)</Label>
                  <Input
                    id="bodyFat"
                    type="number"
                    value={metrics.bodyFat}
                    onChange={(e) => handleMetricChange("bodyFat", e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="muscleMass">Muscle Mass (kg)</Label>
                <Input
                  id="muscleMass"
                  type="number"
                  value={metrics.muscleMass}
                  onChange={(e) => handleMetricChange("muscleMass", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Ruler className="w-4 h-4" />
                  Body Measurements (cm)
                </Label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="waist" className="text-sm">
                      Waist
                    </Label>
                    <Input
                      id="waist"
                      type="number"
                      value={metrics.waist}
                      onChange={(e) => handleMetricChange("waist", e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="chest" className="text-sm">
                      Chest
                    </Label>
                    <Input
                      id="chest"
                      type="number"
                      value={metrics.chest}
                      onChange={(e) => handleMetricChange("chest", e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="arms" className="text-sm">
                      Arms
                    </Label>
                    <Input
                      id="arms"
                      type="number"
                      value={metrics.arms}
                      onChange={(e) => handleMetricChange("arms", e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="thighs" className="text-sm">
                      Thighs
                    </Label>
                    <Input
                      id="thighs"
                      type="number"
                      value={metrics.thighs}
                      onChange={(e) => handleMetricChange("thighs", e.target.value)}
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="notes">Notes & Observations</Label>
                <Textarea
                  id="notes"
                  placeholder="How are you feeling? Any changes you've noticed?"
                  value={metrics.notes}
                  onChange={(e) => handleMetricChange("notes", e.target.value)}
                  className="mt-1"
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Goals & Targets */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-emerald-600" />
                Goals & Targets
              </CardTitle>
              <CardDescription>Set and update your fitness goals</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="targetWeight">Target Weight (kg)</Label>
                <Input
                  id="targetWeight"
                  type="number"
                  value={goals.targetWeight}
                  onChange={(e) => handleGoalChange("targetWeight", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="targetBodyFat">Target Body Fat (%)</Label>
                <Input
                  id="targetBodyFat"
                  type="number"
                  value={goals.targetBodyFat}
                  onChange={(e) => handleGoalChange("targetBodyFat", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="targetDate" className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Target Date
                </Label>
                <Input
                  id="targetDate"
                  type="date"
                  value={goals.targetDate}
                  onChange={(e) => handleGoalChange("targetDate", e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="weeklyGoal">Weekly Goal</Label>
                <Input
                  id="weeklyGoal"
                  value={goals.weeklyGoal}
                  onChange={(e) => handleGoalChange("weeklyGoal", e.target.value)}
                  className="mt-1"
                  placeholder="e.g., Lose 0.5kg per week"
                />
              </div>

              {/* Progress Summary */}
              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Progress Summary
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Weight Progress</span>
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">
                      -7kg from start
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Goal Progress</span>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                      70% complete
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Time Remaining</span>
                    <Badge variant="secondary" className="bg-orange-100 text-orange-700">
                      24 weeks
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} className="bg-emerald-600 hover:bg-emerald-700">
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  )
}

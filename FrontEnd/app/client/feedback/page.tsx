"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Send, MessageSquare, Star, Calendar } from "lucide-react"
import Link from "next/link"

export default function ClientFeedback() {
  const [feedback, setFeedback] = useState("")
  const [rating, setRating] = useState(0)

  const previousFeedback = [
    {
      date: "2024-12-05",
      message:
        "The HIIT workout was challenging but I felt great afterwards. Could use more recovery time between sets.",
      rating: 4,
      trainerResponse: "Great feedback! I'll adjust the rest periods in your next session.",
    },
    {
      date: "2024-11-28",
      message: "Loving the new meal plan! The salmon quinoa bowl is delicious. More recipes like this please.",
      rating: 5,
      trainerResponse: "So glad you're enjoying it! I'll add more fish-based recipes to your plan.",
    },
    {
      date: "2024-11-20",
      message: "Had some difficulty with the deadlift form. Could we review this in our next session?",
      rating: 3,
      trainerResponse: "Form is crucial. Let's dedicate extra time to deadlift technique next week.",
    },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    alert("Feedback submitted successfully!")
    setFeedback("")
    setRating(0)
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
            <h1 className="text-2xl font-bold text-gray-900">Feedback & Communication</h1>
            <p className="text-gray-600">Share your thoughts and communicate with your trainer</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Submit New Feedback */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-emerald-600" />
                Submit Feedback
              </CardTitle>
              <CardDescription>Share your experience and suggestions</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="rating">Rate your recent experience</Label>
                  <div className="flex gap-1 mt-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className={`p-1 ${star <= rating ? "text-yellow-400" : "text-gray-300"} hover:text-yellow-400 transition-colors`}
                      >
                        <Star className="w-6 h-6 fill-current" />
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <Label htmlFor="feedback">Your Feedback</Label>
                  <Textarea
                    id="feedback"
                    placeholder="Share your thoughts about workouts, meal plans, or any suggestions..."
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    className="mt-1"
                    rows={5}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  disabled={!feedback.trim() || rating === 0}
                >
                  <Send className="w-4 h-4 mr-2" />
                  Send Feedback
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Previous Feedback */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-emerald-600" />
                Previous Feedback
              </CardTitle>
              <CardDescription>Your feedback history and trainer responses</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {previousFeedback.map((item, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{new Date(item.date).toLocaleDateString()}</span>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`w-4 h-4 ${star <= item.rating ? "text-yellow-400 fill-current" : "text-gray-300"}`}
                          />
                        ))}
                      </div>
                    </div>

                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-sm">{item.message}</p>
                    </div>

                    {item.trainerResponse && (
                      <div className="bg-emerald-50 p-3 rounded border-l-4 border-emerald-500">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="secondary" className="bg-emerald-100 text-emerald-700 text-xs">
                            Trainer Response
                          </Badge>
                        </div>
                        <p className="text-sm text-emerald-800">{item.trainerResponse}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

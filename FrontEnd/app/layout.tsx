import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { ReduxProvider } from "@/components/redux-provider"
import { AuthProvider } from "@/components/auth-provider"
import { AppContent } from "@/components/app-content"

export const metadata: Metadata = {
  title: "TrainerPro Dashboard",
  description: "Professional fitness trainer management platform",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        <ReduxProvider>
          <AuthProvider>
            <AppContent>{children}</AppContent>
          </AuthProvider>
        </ReduxProvider>
        <Analytics />
      </body>
    </html>
  )
}

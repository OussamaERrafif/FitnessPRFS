'use client'

import { usePathname } from 'next/navigation'
import { Sidebar } from "@/components/sidebar"
import { TopNav } from "@/components/top-nav"
import { Suspense } from "react"

export function AppContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  
  // Check if current path is an auth page
  const isAuthPage = pathname === '/login' || pathname === '/register'
  
  if (isAuthPage) {
    // Return just the children without sidebar/header for auth pages
    return <>{children}</>
  }
  
  // Return the full app layout for authenticated pages
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Suspense fallback={<div>Loading...</div>}>
          <TopNav />
        </Suspense>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  )
}

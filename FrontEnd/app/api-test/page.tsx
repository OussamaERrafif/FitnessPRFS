'use client'

import React from 'react'
import { Provider } from 'react-redux'
import { store } from '@/lib/store/store'
import ApiTestComponent from './api-test-component'
import CookieDebug from './cookie-debug'
import AuthDebug from './auth-debug'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function ApiTestPage() {
  return (
    <Provider store={store}>
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">API Test Page</h1>
        
        <Tabs defaultValue="api" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="api">API Tests</TabsTrigger>
            <TabsTrigger value="cookies">Cookie Debug</TabsTrigger>
            <TabsTrigger value="auth">Auth Debug</TabsTrigger>
          </TabsList>
          <TabsContent value="api">
            <ApiTestComponent />
          </TabsContent>
          <TabsContent value="cookies">
            <CookieDebug />
          </TabsContent>
          <TabsContent value="auth">
            <AuthDebug />
          </TabsContent>
        </Tabs>
      </div>
    </Provider>
  )
}

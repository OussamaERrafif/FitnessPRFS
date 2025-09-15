'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import {
  useGetClientsQuery,
  useCreateClientMutation,
  useDeleteClientMutation,
  type Client,
} from '@/lib/store/fitness-api'

export function ClientsExample() {
  const { toast } = useToast()
  const [newClientName, setNewClientName] = useState('')
  const [newClientEmail, setNewClientEmail] = useState('')

  // RTK Query hooks
  const {
    data: clients = [],
    error,
    isLoading,
    refetch,
  } = useGetClientsQuery()

  const [createClient, { isLoading: isCreating }] = useCreateClientMutation()
  const [deleteClient] = useDeleteClientMutation()

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newClientName.trim() || !newClientEmail.trim()) return

    try {
      await createClient({
        name: newClientName.trim(),
        email: newClientEmail.trim(),
      }).unwrap()

      setNewClientName('')
      setNewClientEmail('')
      toast({
        title: 'Success',
        description: 'Client created successfully',
      })
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to create client',
        variant: 'destructive',
      })
    }
  }

  const handleDeleteClient = async (clientId: string, clientName: string) => {
    try {
      await deleteClient(clientId).unwrap()
      toast({
        title: 'Success',
        description: `${clientName} deleted successfully`,
      })
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to delete client',
        variant: 'destructive',
      })
    }
  }

  if (isLoading) {
    return <div className="p-4">Loading clients...</div>
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-red-500 mb-4">Error loading clients</div>
        <Button onClick={() => refetch()}>Retry</Button>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Add New Client</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreateClient} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={newClientName}
                onChange={(e) => setNewClientName(e.target.value)}
                placeholder="Enter client name"
                required
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={newClientEmail}
                onChange={(e) => setNewClientEmail(e.target.value)}
                placeholder="Enter client email"
                required
              />
            </div>
            <Button type="submit" disabled={isCreating}>
              {isCreating ? 'Creating...' : 'Create Client'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Clients List ({clients.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {clients.length === 0 ? (
            <p className="text-muted-foreground">No clients found</p>
          ) : (
            <div className="space-y-2">
              {clients.map((client: Client) => (
                <div
                  key={client.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <h3 className="font-medium">{client.name}</h3>
                    <p className="text-sm text-muted-foreground">{client.email}</p>
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeleteClient(client.id, client.name)}
                  >
                    Delete
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

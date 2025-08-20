import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bot, Plus, Smartphone } from 'lucide-react'

export default function TelegramPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Telegram Sessions</h1>
          <p className="text-muted-foreground">
            Manage your Telegram API connections and authentication
          </p>
        </div>
        
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add New Session
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bot className="mr-2 h-5 w-5" />
              Setup Instructions
            </CardTitle>
            <CardDescription>
              Connect your Telegram account to start automation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm">1. Get your API credentials from my.telegram.org</p>
              <p className="text-sm">2. Enter your phone number</p>
              <p className="text-sm">3. Verify with the code sent to your Telegram</p>
              <p className="text-sm">4. Complete 2FA if enabled</p>
            </div>
            <Button variant="outline" className="w-full">
              <Smartphone className="mr-2 h-4 w-4" />
              Start Setup
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>No Active Sessions</CardTitle>
            <CardDescription>
              You haven't connected any Telegram accounts yet
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <Bot className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-4 text-sm text-muted-foreground">
                Add your first Telegram session to begin
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
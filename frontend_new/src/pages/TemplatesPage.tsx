import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText, Plus, Edit, Trash2 } from 'lucide-react'

export default function TemplatesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Message Templates</h1>
          <p className="text-muted-foreground">
            Create and manage your message templates
          </p>
        </div>
        
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Template
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Getting Started
            </CardTitle>
            <CardDescription>
              Create your first message template
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm">
                Templates help you send consistent messages across all your groups. 
                You can use variables, formatting, and even emojis.
              </p>
              <Button variant="outline" className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Create Template
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>No Templates</CardTitle>
            <CardDescription>
              You haven't created any templates yet
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-4 text-sm text-muted-foreground">
                Start by creating your first template
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
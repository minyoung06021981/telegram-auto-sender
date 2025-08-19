import { MessageSquare } from 'lucide-react'

export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <MessageSquare className="h-12 w-12 text-primary animate-pulse" />
          <div className="absolute -inset-1 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
        </div>
        
        <div className="text-center">
          <h2 className="text-lg font-semibold">Loading...</h2>
          <p className="text-sm text-muted-foreground">
            Please wait while we load your dashboard
          </p>
        </div>
      </div>
    </div>
  )
}
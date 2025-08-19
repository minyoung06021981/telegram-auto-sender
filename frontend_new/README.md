# 🎨 Telegram Auto Sender Frontend V2.0

Modern React application built with TypeScript, Vite, and 2025 best practices.

## 🚀 Technologies

- **React 18** - Modern React with hooks & concurrent features
- **TypeScript** - Full type safety
- **Vite** - Fast build tool & dev server
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state management
- **React Router V7** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Modern component library
- **React Hook Form** - Performant form handling
- **Zod** - Schema validation

## 🏗️ Architecture

```
src/
├── components/          # Reusable components
│   ├── ui/             # Base UI components (shadcn/ui)
│   ├── layout/         # Layout components
│   └── common/         # Common components
├── pages/              # Page components
├── stores/             # Zustand state stores
├── api/                # API client & endpoints
├── types/              # TypeScript definitions
├── lib/                # Utility functions
├── hooks/              # Custom React hooks
├── App.tsx             # Main application
└── main.tsx            # Entry point
```

## 🚀 Quick Start

1. **Install dependencies:**
```bash
yarn install
```

2. **Configure environment:**
```bash
cp .env.example .env.local
# Edit .env.local with your backend URL
```

3. **Start development server:**
```bash
yarn dev
```

The app will be available at http://localhost:3000

## 🔧 Available Scripts

- `yarn dev` - Start development server
- `yarn build` - Build for production
- `yarn preview` - Preview production build
- `yarn lint` - Run ESLint
- `yarn type-check` - Run TypeScript checks

## 🎯 State Management with Zustand

Modern, lightweight state management:

```typescript
// Clean, typed stores
export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (credentials) => {
        const response = await authApi.login(credentials)
        set({
          user: response.user,
          token: response.access_token,
          isAuthenticated: true
        })
      }
    }),
    { name: 'auth-storage' }
  )
)
```

## 🎨 Design System

Built with **shadcn/ui** for consistency:

- **Theming** - Light/Dark mode support
- **Components** - Pre-built, accessible components
- **Styling** - Tailwind CSS utilities
- **Icons** - Lucide React icon library
- **Typography** - Consistent text styles

### Theme System
```typescript
// Automatic theme switching
const { theme, setTheme } = useAppStore()

// Supports: 'light', 'dark', 'system'
setTheme('dark')
```

## 🔒 Authentication & Security

### Protected Routes
```typescript
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}
```

### API Security
- **JWT tokens** automatically attached to requests
- **Token refresh** handling
- **Error boundaries** for graceful failures
- **Input validation** with Zod schemas

## 📱 Responsive Design

Mobile-first approach:

- **Breakpoints** - Tailwind responsive utilities
- **Sidebar** - Collapsible navigation
- **Touch-friendly** - Appropriate sizing
- **Performance** - Optimized for mobile devices

## 🚀 Performance Optimizations

### Code Splitting
```typescript
// Lazy load pages
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
```

### Caching
- **TanStack Query** for server state caching
- **Zustand persist** for local state
- **Service worker** ready for offline support

### Bundle Optimization
- **Tree shaking** with ES modules
- **Dynamic imports** for code splitting
- **Asset optimization** with Vite

## 🧪 Testing Strategy

Ready for comprehensive testing:

```bash
# Component tests
yarn test

# E2E tests (Playwright ready)
yarn test:e2e

# Type checking
yarn type-check
```

Testing setup includes:
- **React Testing Library** for component tests
- **Playwright** for E2E tests
- **MSW** for API mocking
- **Vitest** for unit tests

## 🔄 API Integration

Type-safe API client:

```typescript
// Strongly typed API calls
const { data, isLoading, error } = useQuery({
  queryKey: ['groups'],
  queryFn: () => groupsApi.getGroups(),
})
```

### Error Handling
- **Global error boundaries**
- **Toast notifications** for user feedback
- **Retry mechanisms** with TanStack Query
- **Offline handling** ready

## 📊 Features

### Implemented Pages
- ✅ **Login/Register** - Authentication flows
- ✅ **Dashboard** - Overview & statistics
- ✅ **Telegram** - Session management
- ✅ **Groups** - Group management interface
- ✅ **Templates** - Message templates
- ✅ **Settings** - User preferences

### UI Components
- ✅ **Navigation** - Sidebar with collapsible menu
- ✅ **Header** - User menu & theme toggle
- ✅ **Forms** - Validated forms with error handling
- ✅ **Cards** - Consistent data display
- ✅ **Modals** - Accessible dialog system
- ✅ **Notifications** - Toast system

## 🎨 Styling Guidelines

### Tailwind Classes
```typescript
// Consistent component styling
className={cn(
  "base-styles",
  variant === "primary" && "variant-styles",
  className // Allow override
)}
```

### CSS Variables
```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --background: 0 0% 100%;
  /* ... theme variables */
}
```

## 🔮 Future Enhancements

Ready for:
- **PWA** - Service worker & offline support
- **Real-time** - WebSocket integration
- **Animations** - Framer Motion integration
- **Internationalization** - i18n ready
- **A/B Testing** - Feature flag system

## 📈 Performance Metrics

Optimized for:
- **First Contentful Paint** < 1.5s
- **Largest Contentful Paint** < 2.5s
- **Time to Interactive** < 3s
- **Bundle size** < 200KB gzipped

## 🚀 Deployment

### Build for Production
```bash
yarn build
```

### Environment Variables
```env
VITE_API_URL=https://api.yourapp.com/api
VITE_APP_ENV=production
```

### Deployment Platforms
- **Vercel** - Zero-config deployment
- **Netlify** - Continuous deployment
- **Docker** - Containerized deployment
- **Static hosting** - Any static host

## 🔄 Migration from V1

Smooth migration path:
- **Feature parity** - All V1 features available
- **Improved UX** - Better user experience
- **Type safety** - Fewer runtime errors
- **Performance** - Faster loading & interactions

---

Built with ❤️ using modern React best practices
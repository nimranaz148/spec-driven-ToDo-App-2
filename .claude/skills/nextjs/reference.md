# Next.js Reference Guide

## Table of Contents
1. [Server Actions](#server-actions)
2. [Authentication Patterns](#authentication-patterns)
3. [State Management](#state-management)
4. [Performance](#performance)
5. [Deployment](#deployment)

---

## Server Actions

### Basic Server Action
```typescript
// app/actions.ts
"use server"

import { revalidatePath } from "next/cache"
import { api } from "@/lib/api"

export async function createTask(formData: FormData) {
  const title = formData.get("title") as string
  const userId = formData.get("userId") as string

  await api.createTask(userId, { title })
  revalidatePath("/")
}
```

### Server Action with Validation
```typescript
// app/actions.ts
"use server"

import { z } from "zod"

const taskSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
})

export async function createTask(prevState: any, formData: FormData) {
  const userId = formData.get("userId") as string
  const data = {
    title: formData.get("title"),
    description: formData.get("description"),
  }

  const result = taskSchema.safeParse(data)

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors }
  }

  await api.createTask(userId, result.data)
  revalidatePath("/")
  return { success: true }
}
```

### Using Server Actions in Forms
```typescript
// components/TaskForm.tsx
"use client"

import { useFormState, useFormStatus } from "react-dom"
import { createTask } from "@/app/actions"

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? "Adding..." : "Add Task"}
    </button>
  )
}

export function TaskForm({ userId }: { userId: string }) {
  const [state, formAction] = useFormState(
    createTask.bind(null, userId),
    null
  )

  return (
    <form action={formAction} className="space-y-4">
      <input type="hidden" name="userId" value={userId} />
      <input
        name="title"
        type="text"
        placeholder="Task title"
        className="border p-2 w-full"
        required
      />
      <SubmitButton />
      {state?.errors?.title && (
        <p className="text-red-500">{state.errors.title}</p>
      )}
    </form>
  )
}
```

---

## Authentication Patterns

### Better Auth Setup
```typescript
// lib/auth.ts
import { createAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = createAuth({
  plugins: [
    jwt({
      jwt: {
        secret: process.env.BETTER_AUTH_SECRET!,
        expiry: "7d",
      },
    }),
  ],
  providers: {
    credentials: {
      providerName: "credentials",
      credentials: {
        email: { type: "email", label: "Email" },
        password: { type: "password", label: "Password" },
      },
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
})
```

### Auth Provider Component
```typescript
// components/AuthProvider.tsx
"use client"

import { AuthProvider } from "better-auth/react"
import { auth } from "@/lib/auth"

export function AuthProviderWrapper({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider auth={auth}>
      {children}
    </AuthProvider>
  )
}
```

### Using Session in Components
```typescript
// components/Header.tsx
"use client"

import { useSession, signIn, signOut } from "better-auth/react"

export function Header() {
  const { data: session, isLoading } = useSession()

  if (isLoading) return null

  return (
    <header className="flex justify-between items-center p-4 border-b">
      <h1 className="text-xl font-bold">Todo App</h1>
      {session ? (
        <div className="flex items-center gap-4">
          <span>{session.user.name}</span>
          <button
            onClick={() => signOut()}
            className="text-red-500"
          >
            Sign Out
          </button>
        </div>
      ) : (
        <button
          onClick={() => signIn("google")}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Sign In
        </button>
      )}
    </header>
  )
}
```

### Protected Route Pattern
```typescript
// app/protected/page.tsx
import { getServerSession } from "better-auth/server"
import { redirect } from "next/navigation"

export default async function ProtectedPage() {
  const session = await getServerSession()

  if (!session) {
    redirect("/auth/signin?callbackUrl=/protected")
  }

  return <div>Protected content for {session.user.name}</div>
}
```

---

## State Management

### useState for Local State
```typescript
"use client"

import { useState } from "react"

export function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

### useEffect for Data Fetching
```typescript
"use client"

import { useEffect, useState } from "react"
import { api, Task } from "@/lib/api"

export function TaskList({ userId }: { userId: string }) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadTasks() {
      try {
        const data = await api.getTasks(userId)
        setTasks(data)
      } finally {
        setLoading(false)
      }
    }

    loadTasks()
  }, [userId])

  if (loading) return <div>Loading...</div>

  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  )
}
```

### Optimistic Updates
```typescript
"use client"

import { useOptimistic } from "react"

export function TaskItem({ task, onToggle }: TaskItemProps) {
  const [optimisticTask, setOptimisticTask] = useOptimistic(
    task,
    (state, completed: boolean) => ({ ...state, completed })
  )

  async function handleToggle() {
    setOptimisticTask(!task.completed)
    await onToggle(task.id)
  }

  return (
    <li className={optimisticTask.completed ? "line-through" : ""}>
      <input
        type="checkbox"
        checked={optimisticTask.completed}
        onChange={handleToggle}
      />
      {optimisticTask.title}
    </li>
  )
}
```

---

## Performance

### Image Optimization
```typescript
import Image from "next/image"

export function UserAvatar({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={40}
      height={40}
      className="rounded-full"
      priority // Load immediately
    />
  )
}
```

### Dynamic Imports
```typescript
import dynamic from "next/dynamic"

const HeavyComponent = dynamic(
  () => import("@/components/HeavyComponent"),
  {
    loading: () => <p>Loading...</p>,
    ssr: false, // Disable SSR for client-only components
  }
)
```

### Static Generation
```typescript
// app/about/page.tsx
export const dynamic = "force-static"

export async function generateStaticParams() {
  return [{ locale: "en" }, { locale: "es" }]
}

export default function AboutPage() {
  return <div>About page (statically generated)</div>
}
```

---

## Deployment

### Vercel Deployment

1. Connect your GitHub repository to Vercel
2. Configure build command: `npm run build`
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `BETTER_AUTH_SECRET`
   - OAuth provider credentials

### Environment Variables
```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-dev-secret

# Vercel (production)
NEXT_PUBLIC_API_URL=https://your-api.vercel.app
BETTER_AUTH_SECRET=your-production-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Docker
```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

### Production Checklist
- [ ] Set `NEXT_PUBLIC_API_URL` to production API
- [ ] Configure OAuth redirects for production domain
- [ ] Enable proper CORS on backend
- [ ] Set up error boundaries
- [ ] Configure proper caching headers
- [ ] Monitor bundle size with `@next/bundle-analyzer`
- [ ] Use `next/image` for optimized images
- [ ] Implement proper loading states

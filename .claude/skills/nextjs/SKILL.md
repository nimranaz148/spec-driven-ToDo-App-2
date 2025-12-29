---
name: nextjs
description: Next.js 16+ App Router patterns and best practices. Use when building pages, components, or configuring Next.js application for the Todo frontend.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Next.js Skill

## Quick Reference

Next.js 16+ with App Router is the recommended approach for React applications.

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page (server component)
│   └── (routes)/
│       ├── auth/
│       │   └── signin/
│       │       └── page.tsx
│       └── tasks/
│           └── page.tsx
├── components/
│   ├── TaskList.tsx
│   └── TaskForm.tsx
├── lib/
│   ├── api.ts
│   └── auth.ts
├── types/
│   └── index.ts
└── public/
```

## Server Components

```typescript
// app/page.tsx (Server Component by default)
import { getServerSession } from "better-auth/server"
import { redirect } from "next/navigation"
import { TaskList } from "@/components/TaskList"

export default async function DashboardPage() {
  const session = await getServerSession()

  if (!session) {
    redirect("/auth/signin")
  }

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">My Tasks</h1>
      <TaskList userId={session.user.id} />
    </main>
  )
}
```

## Client Components

```typescript
// components/TaskForm.tsx
"use client"

import { useState } from "react"
import { api } from "@/lib/api"

interface TaskFormProps {
  userId: string
  onTaskCreated: () => void
}

export function TaskForm({ userId, onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      await api.createTask(userId, { title })
      setTitle("")
      onTaskCreated()
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="border p-2 rounded flex-1"
        placeholder="Add a new task..."
        required
      />
      <button
        type="submit"
        disabled={loading || !title.trim()}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? "Adding..." : "Add Task"}
      </button>
    </form>
  )
}
```

## API Routes (Optional)

```typescript
// app/api/tasks/route.ts
import { NextResponse } from "next/server"
import { getServerSession } from "better-auth/server"

export async function GET() {
  const session = await getServerSession()
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const tasks = await fetchTasks(session.user.id)
  return NextResponse.json(tasks)
}
```

## Styling with Tailwind

```typescript
// Common patterns
<div className="container mx-auto p-4">Container with padding</div>
<div className="flex items-center gap-4">Flex layout</div>
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">Responsive grid</div>
<button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Button</button>
<input className="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500">Input</input>
```

## Data Fetching

```typescript
// lib/api.ts (used in client components)
class ApiClient {
  async getTasks(userId: string): Promise<Task[]> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      }
    )
    if (!response.ok) throw new Error("Failed to fetch tasks")
    return response.json()
  }
}

export const api = new ApiClient()
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-here
```

## Running the App

```bash
npm run dev    # Development with hot reload
npm run build  # Production build
npm start      # Production server
```

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Advanced routing patterns
- Server actions
- Authentication patterns
- Performance optimization
- Deployment options

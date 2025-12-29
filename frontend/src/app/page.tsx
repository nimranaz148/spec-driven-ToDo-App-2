'use client';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { TaskList } from '@/components/tasks/task-list';

export default function HomePage() {
  return (
    <ProtectedRoute>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold mb-2">My Tasks</h1>
          <p className="text-muted-foreground">Stay organized and get things done</p>
        </div>
        <TaskList />
      </div>
    </ProtectedRoute>
  );
}

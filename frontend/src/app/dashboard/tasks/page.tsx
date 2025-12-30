'use client';

import { TaskList } from '@/components/tasks/task-list';

export default function TasksPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold">All Tasks</h1>
        <p className="text-muted-foreground mt-1">
          Manage all your tasks in one place
        </p>
      </div>
      <TaskList />
    </div>
  );
}

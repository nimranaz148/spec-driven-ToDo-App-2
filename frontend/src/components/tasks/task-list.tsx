'use client';

import { useEffect, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/auth-store';
import { useTaskStore } from '@/stores/task-store';
import { TaskItem } from './task-item';
import { TaskForm } from './task-form';
import { EmptyState } from './empty-state';
import { TaskListSkeleton } from './skeleton';
import { cn } from '@/lib/utils';

export function TaskList() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const { user, token, isAuthenticated } = useAuthStore();
  const { tasks, total, setTasks, setLoading, setError: setStoreError } = useTaskStore();

  useEffect(() => {
    const fetchTasks = async () => {
      if (!user || !token) {
        setLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const completed = filter === 'active' ? false : filter === 'completed' ? true : undefined;
        const data = await api.getTasks(user.id, completed);
        setTasks(data.tasks, data.total);
      } catch {
        setError('Failed to load tasks');
        setStoreError('Failed to load tasks');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [user, token, filter, setTasks, setLoading, setStoreError]);

  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  if (!isAuthenticated || !user) {
    return (
      <EmptyState
        title="Please log in"
        description="Log in to view and manage your tasks"
      />
    );
  }

  if (isLoading) {
    return <TaskListSkeleton count={3} />;
  }

  if (error) {
    return (
      <EmptyState
        title="Error loading tasks"
        description={error}
      />
    );
  }

  const getEmptyMessage = () => {
    switch (filter) {
      case 'active':
        return { title: 'No active tasks', description: 'All tasks are completed!' };
      case 'completed':
        return { title: 'No completed tasks', description: 'Complete a task to see it here' };
      default:
        return { title: 'No tasks yet', description: 'Create your first task above to get started' };
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <section aria-labelledby="create-task-heading">
        <h2 id="create-task-heading" className="sr-only">Create new task</h2>
        <TaskForm
          onSuccess={() => setFilter('all')}
          onError={setError}
        />
      </section>

      <div
        role="tablist"
        aria-label="Filter tasks"
        className="flex flex-wrap gap-2 border-b pb-2"
      >
        <button
          role="tab"
          aria-selected={filter === 'all'}
          aria-controls="task-list"
          onClick={() => setFilter('all')}
          className={cn(
            "touch-target px-3 sm:px-4 py-2 text-sm font-medium rounded-md transition-colors min-h-[44px]",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            filter === 'all'
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground hover:bg-muted"
          )}
        >
          All <span className="ml-1 text-xs">({total})</span>
        </button>
        <button
          role="tab"
          aria-selected={filter === 'active'}
          aria-controls="task-list"
          onClick={() => setFilter('active')}
          className={cn(
            "touch-target px-3 sm:px-4 py-2 text-sm font-medium rounded-md transition-colors min-h-[44px]",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            filter === 'active'
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground hover:bg-muted"
          )}
        >
          Active <span className="ml-1 text-xs">({tasks.filter(t => !t.completed).length})</span>
        </button>
        <button
          role="tab"
          aria-selected={filter === 'completed'}
          aria-controls="task-list"
          onClick={() => setFilter('completed')}
          className={cn(
            "touch-target px-3 sm:px-4 py-2 text-sm font-medium rounded-md transition-colors min-h-[44px]",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            filter === 'completed'
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground hover:bg-muted"
          )}
        >
          Completed <span className="ml-1 text-xs">({tasks.filter(t => t.completed).length})</span>
        </button>
      </div>

      <section
        id="task-list"
        role="tabpanel"
        aria-label={`${filter} tasks`}
      >
        {filteredTasks.length === 0 ? (
          <EmptyState {...getEmptyMessage()} />
        ) : (
          <AnimatePresence mode="popLayout">
            <div className="space-y-3" role="list">
              {filteredTasks.map((task) => (
                <TaskItem key={task.id} task={task} />
              ))}
            </div>
          </AnimatePresence>
        )}
      </section>
    </div>
  );
}

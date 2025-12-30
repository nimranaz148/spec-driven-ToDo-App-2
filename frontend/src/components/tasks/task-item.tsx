'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/stores/auth-store';
import { useTaskStore } from '@/stores/task-store';
import { cn, formatDate } from '@/lib/utils';
import type { Task } from '@/lib/types';
import { TaskCard } from './task-card';
import { Checkbox } from '@/components/ui/checkbox';
import { EditTaskDialog } from './edit-task-dialog';

interface TaskItemProps {
  task: Task;
}

export function TaskItem({ task }: TaskItemProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const { user, token } = useAuthStore();
  const { toggleComplete, deleteTask } = useTaskStore();

  const handleToggle = async () => {
    if (!user || !token || isLoading) return;

    setIsLoading(true);
    try {
      // Use optimistic update from store
      await toggleComplete(task.id);
    } catch (error) {
      console.error('Failed to toggle task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!user || !token || isLoading) return;

    setIsLoading(true);
    try {
      // Use optimistic update from store
      await deleteTask(task.id);
    } catch (error) {
      console.error('Failed to delete task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: -100, scale: 0.9 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 30,
      }}
    >
      <TaskCard
        className={cn(
          'group transition-all duration-200',
          task.completed && 'bg-muted/30',
          isLoading && 'opacity-60 pointer-events-none'
        )}
        role="article"
        aria-label={`Task: ${task.title}`}
      >
        <div className="flex items-start gap-3">
          <div className="touch-target flex items-center justify-center">
            <Checkbox
              checked={task.completed}
              onCheckedChange={handleToggle}
              disabled={isLoading}
              className="mt-1"
              aria-label={task.completed ? 'Mark task as incomplete' : 'Mark task as complete'}
            />
          </div>

          <div className="flex-1 min-w-0">
            <motion.h3
              className={cn(
                'font-medium transition-all duration-200',
                task.completed && 'line-through text-muted-foreground'
              )}
              animate={{
                opacity: task.completed ? 0.6 : 1,
              }}
            >
              {task.title}
            </motion.h3>
            {task.description && (
              <motion.p
                className={cn(
                  'text-sm text-muted-foreground mt-1',
                  task.completed && 'line-through'
                )}
                animate={{
                  opacity: task.completed ? 0.5 : 0.7,
                }}
              >
                {task.description}
              </motion.p>
            )}
            <p className="text-xs text-muted-foreground mt-2" aria-label={`Created on ${formatDate(task.created_at)}`}>
              Created {formatDate(task.created_at)}
            </p>
          </div>

          <div className="flex items-center gap-1">
            {/* Edit Button */}
            <button
              onClick={() => setIsEditOpen(true)}
              disabled={isLoading}
              className="touch-target opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium text-primary ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-primary/10 h-10 w-10 min-h-[44px] min-w-[44px] p-0"
              aria-label={`Edit task: ${task.title}`}
              type="button"
            >
              <svg
                className="h-4 w-4 sm:h-5 sm:w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>

            {/* Delete Button */}
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="touch-target opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium text-destructive ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-destructive/10 h-10 w-10 min-h-[44px] min-w-[44px] p-0"
              aria-label={`Delete task: ${task.title}`}
              type="button"
            >
              <svg
                className="h-4 w-4 sm:h-5 sm:w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          {/* Edit Task Dialog */}
          <EditTaskDialog
            task={task}
            open={isEditOpen}
            onOpenChange={setIsEditOpen}
          />
        </div>
      </TaskCard>
    </motion.div>
  );
}

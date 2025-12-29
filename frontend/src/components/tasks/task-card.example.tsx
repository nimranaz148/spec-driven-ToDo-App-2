/**
 * TaskCard Component Usage Examples
 *
 * This file demonstrates different ways to use the TaskCard wrapper component.
 */

import { TaskCard, TaskCardHeader, TaskCardContent, TaskCardFooter } from './task-card';

// Example 1: Basic usage (as used in TaskItem)
export function BasicTaskCard() {
  return (
    <TaskCard>
      <div className="flex items-start gap-3">
        <input type="checkbox" className="mt-1" />
        <div className="flex-1">
          <h3 className="font-medium">Task Title</h3>
          <p className="text-sm text-muted-foreground">Task description</p>
        </div>
      </div>
    </TaskCard>
  );
}

// Example 2: Using sub-components for structured layout
export function StructuredTaskCard() {
  return (
    <TaskCard>
      <TaskCardHeader>
        <h3 className="font-semibold">Project Planning</h3>
        <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">High Priority</span>
      </TaskCardHeader>

      <TaskCardContent>
        <p className="text-sm text-muted-foreground">
          Complete the initial project planning and set up the development environment.
        </p>
        <div className="flex gap-2 text-xs text-muted-foreground">
          <span>Due: Tomorrow</span>
          <span>•</span>
          <span>3 subtasks</span>
        </div>
      </TaskCardContent>

      <TaskCardFooter>
        <div className="flex gap-2">
          <button className="text-xs hover:underline">Edit</button>
          <button className="text-xs hover:underline">Archive</button>
        </div>
        <button className="text-xs text-destructive hover:underline">Delete</button>
      </TaskCardFooter>
    </TaskCard>
  );
}

// Example 3: Custom styling with className
export function CustomStyledCard() {
  return (
    <TaskCard className="border-l-4 border-l-primary bg-primary/5">
      <div className="space-y-2">
        <h3 className="font-bold text-lg">Important Task</h3>
        <p className="text-sm">This card has custom border and background styling.</p>
      </div>
    </TaskCard>
  );
}

// Example 4: Compact version
export function CompactTaskCard() {
  return (
    <TaskCard className="p-2">
      <div className="flex items-center justify-between">
        <span className="text-sm">Quick task item</span>
        <button className="text-xs text-primary">Complete</button>
      </div>
    </TaskCard>
  );
}

// Example 5: Loading state
export function LoadingTaskCard() {
  return (
    <TaskCard className="animate-pulse">
      <div className="space-y-2">
        <div className="h-4 bg-muted rounded w-3/4" />
        <div className="h-3 bg-muted rounded w-1/2" />
      </div>
    </TaskCard>
  );
}

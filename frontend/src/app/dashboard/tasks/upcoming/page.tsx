'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { CalendarClock, CalendarDays, Trash2, Edit2 } from 'lucide-react';
import { useTaskStore } from '@/stores/task-store';
import { EditTaskDialog } from '@/components/tasks/edit-task-dialog';
import { cn } from '@/lib/utils';
import type { Task } from '@/lib/types';

export default function UpcomingTasksPage() {
  const { tasks, fetchTasks, toggleComplete, deleteTask, isLoading } = useTaskStore();
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Filter upcoming tasks (future dates, not including today)
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const upcomingTasks = tasks
    .filter((t) => {
      if (!t.due_date) return false;
      const dueDate = new Date(t.due_date);
      dueDate.setHours(0, 0, 0, 0);
      return dueDate.getTime() > today.getTime();
    })
    .sort((a, b) => {
      const dateA = new Date(a.due_date!).getTime();
      const dateB = new Date(b.due_date!).getTime();
      return dateA - dateB;
    });

  // Group by date
  const groupedTasks = upcomingTasks.reduce((acc, task) => {
    const date = new Date(task.due_date!).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    });
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <CalendarClock className="h-8 w-8 text-primary" />
          <h1 className="text-2xl sm:text-3xl font-bold">Upcoming Tasks</h1>
        </div>
        <p className="text-muted-foreground">
          {upcomingTasks.length > 0
            ? `${upcomingTasks.length} tasks scheduled for the future`
            : 'No upcoming tasks scheduled'}
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          {[...Array(2)].map((_, i) => (
            <div key={i}>
              <div className="h-6 w-32 bg-muted rounded animate-pulse mb-3" />
              <div className="space-y-3">
                {[...Array(2)].map((_, j) => (
                  <div key={j} className="h-20 bg-muted rounded-lg animate-pulse" />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : Object.keys(groupedTasks).length > 0 ? (
        <div className="space-y-8">
          {Object.entries(groupedTasks).map(([date, dateTasks]) => (
            <div key={date}>
              <div className="flex items-center gap-2 mb-4">
                <CalendarDays className="h-4 w-4 text-muted-foreground" />
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  {date}
                </h2>
                <Badge variant="secondary" className="ml-2">
                  {dateTasks.length} task{dateTasks.length !== 1 && 's'}
                </Badge>
              </div>
              <div className="space-y-3">
                {dateTasks.map((task) => (
                  <Card
                    key={task.id}
                    className={cn(
                      'border-border/50 transition-all duration-200',
                      task.completed && 'opacity-60'
                    )}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-4">
                        <Checkbox
                          checked={task.completed}
                          onCheckedChange={() => toggleComplete(task.id)}
                          className="mt-1"
                        />
                        <div className="flex-1 min-w-0">
                          <p
                            className={cn(
                              'font-medium',
                              task.completed && 'line-through text-muted-foreground'
                            )}
                          >
                            {task.title}
                          </p>
                          {task.description && (
                            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                              {task.description}
                            </p>
                          )}
                          <div className="flex items-center gap-2 mt-2">
                            {task.priority && (
                              <Badge
                                variant="outline"
                                className={cn(
                                  'text-xs',
                                  task.priority === 'high' && 'border-red-500 text-red-500',
                                  task.priority === 'medium' && 'border-yellow-500 text-yellow-500',
                                  task.priority === 'low' && 'border-green-500 text-green-500'
                                )}
                              >
                                {task.priority}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setEditingTask(task)}
                            className="h-8 w-8"
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => deleteTask(task.id)}
                            className="h-8 w-8 text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <Card className="border-border/50">
          <CardContent className="p-12 text-center">
            <CalendarClock className="h-16 w-16 mx-auto mb-4 text-primary/30" />
            <h3 className="text-lg font-semibold mb-2">No upcoming tasks</h3>
            <p className="text-muted-foreground">
              Schedule some tasks for the future to stay ahead of your work.
            </p>
          </CardContent>
        </Card>
      )}

      {editingTask && (
        <EditTaskDialog
          task={editingTask}
          open={!!editingTask}
          onOpenChange={(open) => !open && setEditingTask(null)}
        />
      )}
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { CalendarDays, CheckCircle2, Trash2, Edit2 } from 'lucide-react';
import { useTaskStore } from '@/stores/task-store';
import { EditTaskDialog } from '@/components/tasks/edit-task-dialog';
import { cn } from '@/lib/utils';
import type { Task } from '@/lib/types';

export default function TodayTasksPage() {
  const { tasks, fetchTasks, toggleComplete, deleteTask, isLoading } = useTaskStore();
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Filter today's tasks
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const todayTasks = tasks.filter((t) => {
    if (!t.due_date) return false;
    const dueDate = new Date(t.due_date);
    dueDate.setHours(0, 0, 0, 0);
    return dueDate.getTime() === today.getTime();
  });

  const completedCount = todayTasks.filter((t) => t.completed).length;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <CalendarDays className="h-8 w-8 text-primary" />
          <h1 className="text-2xl sm:text-3xl font-bold">Today&apos;s Tasks</h1>
        </div>
        <p className="text-muted-foreground">
          {todayTasks.length > 0
            ? `${completedCount} of ${todayTasks.length} tasks completed`
            : 'No tasks scheduled for today'}
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-muted rounded-lg animate-pulse" />
          ))}
        </div>
      ) : todayTasks.length > 0 ? (
        <div className="space-y-3">
          {todayTasks.map((task) => (
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
      ) : (
        <Card className="border-border/50">
          <CardContent className="p-12 text-center">
            <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-primary/30" />
            <h3 className="text-lg font-semibold mb-2">No tasks for today</h3>
            <p className="text-muted-foreground">
              You&apos;re all caught up. Enjoy your day or add some new tasks.
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

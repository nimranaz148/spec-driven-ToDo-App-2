'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  BarChart3,
  TrendingUp,
  CheckCircle2,
  Clock,
  Calendar,
  Target,
} from 'lucide-react';
import { useTaskStore } from '@/stores/task-store';
import { cn } from '@/lib/utils';

export default function AnalyticsPage() {
  const { tasks, fetchTasks } = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Calculate analytics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.completed).length;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Priority breakdown
  const highPriority = tasks.filter((t) => t.priority === 'high').length;
  const mediumPriority = tasks.filter((t) => t.priority === 'medium').length;
  const lowPriority = tasks.filter((t) => t.priority === 'low').length;
  const noPriority = tasks.filter((t) => !t.priority).length;

  // Completed by priority
  const highCompleted = tasks.filter((t) => t.priority === 'high' && t.completed).length;
  const mediumCompleted = tasks.filter((t) => t.priority === 'medium' && t.completed).length;
  const lowCompleted = tasks.filter((t) => t.priority === 'low' && t.completed).length;

  // Tasks by date
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const overdue = tasks.filter((t) => {
    if (!t.due_date || t.completed) return false;
    const dueDate = new Date(t.due_date);
    dueDate.setHours(0, 0, 0, 0);
    return dueDate.getTime() < today.getTime();
  }).length;

  const dueToday = tasks.filter((t) => {
    if (!t.due_date) return false;
    const dueDate = new Date(t.due_date);
    dueDate.setHours(0, 0, 0, 0);
    return dueDate.getTime() === today.getTime();
  }).length;

  const upcoming = tasks.filter((t) => {
    if (!t.due_date) return false;
    const dueDate = new Date(t.due_date);
    dueDate.setHours(0, 0, 0, 0);
    return dueDate.getTime() > today.getTime();
  }).length;

  // Recent activity (tasks created in last 7 days)
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  const recentlyCreated = tasks.filter((t) => new Date(t.created_at) >= weekAgo).length;

  const priorityData = [
    {
      label: 'High',
      total: highPriority,
      completed: highCompleted,
      color: 'bg-red-500',
      bgColor: 'bg-red-100 dark:bg-red-900/30',
    },
    {
      label: 'Medium',
      total: mediumPriority,
      completed: mediumCompleted,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
    },
    {
      label: 'Low',
      total: lowPriority,
      completed: lowCompleted,
      color: 'bg-green-500',
      bgColor: 'bg-green-100 dark:bg-green-900/30',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="h-8 w-8 text-primary" />
          <h1 className="text-2xl sm:text-3xl font-bold">Analytics</h1>
        </div>
        <p className="text-muted-foreground">
          Track your productivity and task completion metrics
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-border/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completion Rate</p>
                <p className="text-3xl font-bold text-gradient-gold">{completionRate}%</p>
              </div>
              <div className="p-3 rounded-xl bg-primary/10">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">{completedTasks}</p>
              </div>
              <div className="p-3 rounded-xl bg-green-100 dark:bg-green-900/30">
                <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Overdue</p>
                <p className={cn(
                  'text-3xl font-bold',
                  overdue > 0 ? 'text-red-600 dark:text-red-400' : 'text-muted-foreground'
                )}>
                  {overdue}
                </p>
              </div>
              <div className={cn(
                'p-3 rounded-xl',
                overdue > 0 ? 'bg-red-100 dark:bg-red-900/30' : 'bg-muted'
              )}>
                <Clock className={cn(
                  'h-6 w-6',
                  overdue > 0 ? 'text-red-600 dark:text-red-400' : 'text-muted-foreground'
                )} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">This Week</p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{recentlyCreated}</p>
              </div>
              <div className="p-3 rounded-xl bg-blue-100 dark:bg-blue-900/30">
                <Calendar className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Priority Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Priority Breakdown
            </CardTitle>
            <CardDescription>Tasks by priority level</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {priorityData.map((item) => (
              <div key={item.label} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={cn('w-3 h-3 rounded-full', item.color)} />
                    <span className="font-medium">{item.label} Priority</span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {item.completed}/{item.total} completed
                  </span>
                </div>
                <Progress
                  value={item.total > 0 ? (item.completed / item.total) * 100 : 0}
                  className="h-2"
                />
              </div>
            ))}
            {noPriority > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-muted-foreground" />
                    <span className="font-medium">No Priority</span>
                  </div>
                  <span className="text-sm text-muted-foreground">{noPriority} tasks</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Task Status */}
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              Task Status
            </CardTitle>
            <CardDescription>Current task distribution</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Visual representation */}
              <div className="flex h-8 rounded-full overflow-hidden bg-muted">
                {completedTasks > 0 && (
                  <div
                    className="bg-green-500 transition-all duration-500"
                    style={{ width: `${(completedTasks / totalTasks) * 100}%` }}
                  />
                )}
                {pendingTasks > 0 && (
                  <div
                    className="bg-orange-500 transition-all duration-500"
                    style={{ width: `${(pendingTasks / totalTasks) * 100}%` }}
                  />
                )}
              </div>

              {/* Legend */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-green-100/50 dark:bg-green-900/20">
                  <div className="w-4 h-4 rounded-full bg-green-500" />
                  <div>
                    <p className="font-semibold">{completedTasks}</p>
                    <p className="text-xs text-muted-foreground">Completed</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-orange-100/50 dark:bg-orange-900/20">
                  <div className="w-4 h-4 rounded-full bg-orange-500" />
                  <div>
                    <p className="font-semibold">{pendingTasks}</p>
                    <p className="text-xs text-muted-foreground">Pending</p>
                  </div>
                </div>
              </div>

              {/* Schedule breakdown */}
              <div className="pt-4 border-t border-border">
                <h4 className="text-sm font-semibold mb-3">Schedule Overview</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Due Today</span>
                    <span className="font-medium">{dueToday}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Upcoming</span>
                    <span className="font-medium">{upcoming}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className={cn(
                      overdue > 0 ? 'text-red-600 dark:text-red-400' : 'text-muted-foreground'
                    )}>
                      Overdue
                    </span>
                    <span className={cn(
                      'font-medium',
                      overdue > 0 && 'text-red-600 dark:text-red-400'
                    )}>
                      {overdue}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

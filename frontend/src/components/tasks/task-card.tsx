import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface TaskCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
}

/**
 * TaskCard - A reusable card wrapper component for task items
 *
 * Features:
 * - Clean, modern card design with subtle shadows
 * - Smooth hover transitions and effects
 * - Responsive and accessible
 * - Wraps TaskItem content with consistent styling
 */
export function TaskCard({ children, className, ...props }: TaskCardProps) {
  return (
    <div
      {...props}
      className={cn(
        // Base card styles
        "relative rounded-lg border border-border bg-card text-card-foreground",
        // Shadow and hover effects
        "shadow-sm hover:shadow-md transition-all duration-200",
        // Interactive states
        "hover:border-primary/20",
        // Responsive spacing
        "p-4",
        // Custom classes
        className
      )}
    >
      {children}
    </div>
  );
}

/**
 * TaskCardHeader - Optional header section for the card
 */
interface TaskCardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function TaskCardHeader({ children, className }: TaskCardHeaderProps) {
  return (
    <div className={cn("flex items-center justify-between mb-3", className)}>
      {children}
    </div>
  );
}

/**
 * TaskCardContent - Main content area of the card
 */
interface TaskCardContentProps {
  children: ReactNode;
  className?: string;
}

export function TaskCardContent({ children, className }: TaskCardContentProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {children}
    </div>
  );
}

/**
 * TaskCardFooter - Optional footer section for the card
 */
interface TaskCardFooterProps {
  children: ReactNode;
  className?: string;
}

export function TaskCardFooter({ children, className }: TaskCardFooterProps) {
  return (
    <div className={cn("flex items-center justify-between mt-3 pt-3 border-t", className)}>
      {children}
    </div>
  );
}

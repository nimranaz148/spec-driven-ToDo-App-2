'use client';

import { motion } from 'framer-motion';

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  title = 'No tasks yet',
  description = 'Get started by creating your first task',
  action,
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center py-12 sm:py-16 px-4"
    >
      <div className="mb-6 rounded-full bg-muted p-6 sm:p-8">
        <svg
          className="h-12 w-12 sm:h-16 sm:w-16 text-muted-foreground"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>

      <h3 className="text-xl sm:text-2xl font-semibold text-center mb-2">{title}</h3>
      <p className="text-sm sm:text-base text-muted-foreground text-center mb-6 max-w-sm">
        {description}
      </p>

      {action && <div className="mt-2">{action}</div>}
    </motion.div>
  );
}

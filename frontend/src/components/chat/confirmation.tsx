// Confirmation modal component for bulk chat operations

import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { AlertTriangle, Trash2, CheckCircle } from 'lucide-react'

interface ConfirmationRequest {
  action: string
  message: string
  affected_items: Array<{ id: number; title: string }>
  confirm_token: string
}

interface ConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (token: string) => void
  confirmation: ConfirmationRequest | null
  isLoading?: boolean
}

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  confirmation,
  isLoading = false,
}: ConfirmationModalProps) {
  if (!confirmation) return null

  const getActionIcon = () => {
    switch (confirmation.action) {
      case 'delete_all':
        return <Trash2 className="h-6 w-6 text-red-500" />
      case 'complete_all':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      default:
        return <AlertTriangle className="h-6 w-6 text-yellow-500" />
    }
  }

  const getActionColor = () => {
    switch (confirmation.action) {
      case 'delete_all':
        return 'destructive'
      case 'complete_all':
        return 'default'
      default:
        return 'default'
    }
  }

  const getActionText = () => {
    switch (confirmation.action) {
      case 'delete_all':
        return 'Delete All Tasks'
      case 'complete_all':
        return 'Complete All Tasks'
      default:
        return 'Confirm Action'
    }
  }

  const getDescription = () => {
    const count = confirmation.affected_items.length
    switch (confirmation.action) {
      case 'delete_all':
        return count > 0
          ? `This will permanently delete ${count} task${count === 1 ? '' : 's'}. This action cannot be undone.`
          : 'This will delete all your tasks. This action cannot be undone.'
      case 'complete_all':
        return count > 0
          ? `This will mark ${count} task${count === 1 ? '' : 's'} as completed.`
          : 'This will mark all your incomplete tasks as completed.'
      default:
        return confirmation.message
    }
  }

  const handleConfirm = () => {
    onConfirm(confirmation.confirm_token)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            {getActionIcon()}
            {getActionText()}
          </DialogTitle>
          <DialogDescription className="text-left">
            {getDescription()}
          </DialogDescription>
        </DialogHeader>

        {confirmation.affected_items.length > 0 && (
          <div className="max-h-32 overflow-y-auto rounded-md border p-3">
            <p className="text-sm font-medium text-muted-foreground mb-2">
              Affected tasks:
            </p>
            <ul className="space-y-1">
              {confirmation.affected_items.map((item) => (
                <li
                  key={item.id}
                  className="text-sm text-foreground flex items-center gap-2"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground" />
                  {item.title}
                </li>
              ))}
            </ul>
          </div>
        )}

        <DialogFooter className="flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
            className="mt-2 sm:mt-0"
          >
            Cancel
          </Button>
          <Button
            variant={getActionColor() as 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'}
            onClick={handleConfirm}
            disabled={isLoading}
            className="w-full sm:w-auto"
          >
            {isLoading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Processing...
              </>
            ) : (
              <>
                {getActionIcon()}
                Confirm
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

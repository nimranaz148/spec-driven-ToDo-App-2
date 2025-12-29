# Zustand Store - Optimistic Updates

## Overview

The task store (`task-store.ts`) implements optimistic updates for all task operations. This provides instant UI feedback while API calls are in progress, with automatic rollback if the operation fails.

## How It Works

### Optimistic Update Pattern

1. **Save Previous State**: Before making any changes, save the current state for potential rollback
2. **Update UI Immediately**: Apply the change to local state immediately
3. **Make API Call**: Send the request to the backend
4. **Handle Success**: Replace optimistic data with real data from server
5. **Handle Failure**: Rollback to previous state and show error

### Example Flow

```typescript
// User clicks "complete task"
toggleComplete(userId, taskId)
  → UI updates immediately (checkbox checked)
  → API call sent to backend
  → If success: Replace with server data
  → If failure: Rollback (checkbox unchecked) + show error
```

## Store Actions

### 1. createTask(userId, data)

Creates a new task with optimistic UI update.

**Optimistic Behavior:**
- Immediately adds task to list with temporary negative ID
- Replaces with real task (with server ID) on success
- Removes task and shows error on failure

**Usage:**
```typescript
const { createTask } = useTaskStore();
await createTask(user.id, { title: 'New Task', description: 'Details' });
```

### 2. updateTask(userId, taskId, data)

Updates an existing task.

**Optimistic Behavior:**
- Immediately updates task in local state
- Replaces with server data on success
- Reverts changes and shows error on failure

**Usage:**
```typescript
const { updateTask } = useTaskStore();
await updateTask(user.id, taskId, { title: 'Updated Title' });
```

### 3. deleteTask(userId, taskId)

Deletes a task.

**Optimistic Behavior:**
- Immediately removes task from list
- Decrements total count
- Restores task and shows error on failure

**Usage:**
```typescript
const { deleteTask } = useTaskStore();
await deleteTask(user.id, taskId);
```

### 4. toggleComplete(userId, taskId)

Toggles task completion status.

**Optimistic Behavior:**
- Immediately toggles completed state
- Updates with server data on success
- Reverts toggle and shows error on failure

**Usage:**
```typescript
const { toggleComplete } = useTaskStore();
await toggleComplete(user.id, taskId);
```

## Error Handling

Currently uses a simple `alert()` for error notifications. This should be replaced with a proper toast library:

```typescript
// TODO: Replace with toast library
const showErrorToast = (message: string) => {
  console.error('[Task Store Error]:', message);
  alert(message);
};
```

### Recommended Toast Libraries

1. **react-hot-toast**: Lightweight and simple
   ```bash
   npm install react-hot-toast
   ```

2. **sonner**: Beautiful toast notifications
   ```bash
   npm install sonner
   ```

3. **react-toastify**: Feature-rich with customization
   ```bash
   npm install react-toastify
   ```

### Integration Example (react-hot-toast)

```typescript
import toast from 'react-hot-toast';

const showErrorToast = (message: string) => {
  toast.error(message, {
    duration: 4000,
    position: 'top-right',
  });
};
```

## Benefits

1. **Instant Feedback**: Users see changes immediately without waiting for API
2. **Better UX**: App feels faster and more responsive
3. **Graceful Degradation**: Automatic rollback on errors
4. **Consistent State**: Server response is always the source of truth
5. **Error Visibility**: Users are informed when operations fail

## Component Usage

Components should use the optimistic actions instead of directly calling the API:

### Before (Direct API)
```typescript
// ❌ Old way - manual state management
const handleDelete = async () => {
  try {
    await api.deleteTask(userId, taskId);
    removeTask(taskId); // Manual state update
  } catch (error) {
    // Manual error handling
  }
};
```

### After (Optimistic Updates)
```typescript
// ✅ New way - optimistic updates built-in
const { deleteTask } = useTaskStore();

const handleDelete = async () => {
  try {
    await deleteTask(userId, taskId); // Handles everything
  } catch (error) {
    // Error already shown to user
  }
};
```

## Implementation Details

### Temporary IDs

For create operations, temporary negative IDs are used to avoid conflicts:

```typescript
const optimisticTask: Task = {
  id: -Date.now(), // Temporary negative ID
  // ... other fields
};
```

This ensures:
- No collision with real server IDs (which are positive)
- Each temporary ID is unique (uses timestamp)
- Easy to identify optimistic tasks in state

### State Preservation

Previous state is captured using `get()`:

```typescript
const previousTasks = get().tasks;
const previousTotal = get().total;
```

This allows complete rollback to the exact state before the operation.

## Testing Optimistic Updates

### Manual Testing

1. **Slow Network Simulation**:
   - Chrome DevTools → Network → Throttling → Slow 3G
   - Perform task operations
   - Observe instant UI updates

2. **Error Simulation**:
   - Disconnect network
   - Try to create/update/delete tasks
   - Verify UI rolls back and shows error

### Automated Testing

```typescript
// Example test for optimistic create
it('should add task optimistically and update with real data', async () => {
  const { result } = renderHook(() => useTaskStore());

  // Start with empty state
  expect(result.current.tasks).toHaveLength(0);

  // Mock API
  const mockTask = { id: 1, title: 'Test', completed: false };
  api.createTask = jest.fn().mockResolvedValue(mockTask);

  // Create task
  await act(async () => {
    await result.current.createTask('user-1', { title: 'Test' });
  });

  // Task should be in state with real ID
  expect(result.current.tasks).toHaveLength(1);
  expect(result.current.tasks[0].id).toBe(1);
});
```

## Best Practices

1. **Always await**: Even though UI updates immediately, await the promise to handle errors
2. **Don't rely on loading states**: Operations are instant from user perspective
3. **Handle errors gracefully**: Optimistic updates will rollback automatically
4. **Trust the server**: Server response is always applied after success
5. **Use try-catch**: Wrap calls in try-catch for additional error handling

## Future Improvements

1. **Queue Management**: Handle multiple rapid operations
2. **Conflict Resolution**: Handle concurrent updates from different sources
3. **Offline Support**: Queue operations when offline, sync when online
4. **Optimistic Animations**: Smoother transitions for rollbacks
5. **Toast Integration**: Better error notifications

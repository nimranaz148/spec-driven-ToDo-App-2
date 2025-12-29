# Feature: Task CRUD Operations

## User Stories
- As a user, I can create a new task
- As a user, I can view all my tasks
- As a user, I can update a task
- As a user, I can delete a task
- As a user, I can mark a task complete

## Acceptance Criteria

### Create Task
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Task is associated with logged-in user
- Created task is returned with ID and timestamp

### View Tasks
- Only show tasks for current user
- Display title, status, created date
- Support filtering by status (all/pending/completed)

### Update Task
- Title can be updated (1-200 characters)
- Description can be updated (max 1000 characters)
- Only update fields provided in request

### Delete Task
- Task is permanently removed
- Return confirmation of deletion
- Handle task not found gracefully

### Mark Complete
- Toggle completion status
- Return updated task with status

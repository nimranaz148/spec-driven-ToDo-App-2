"""Task service for CRUD operations."""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Task, utc_now_naive
from ..schemas.task import TaskCreate, TaskUpdate


async def get_user_tasks(
    session: AsyncSession,
    user_id: str,
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[Task], int]:
    """Get all tasks for a user with optional filtering."""
    # Base query with user filter
    base_query = select(Task).where(Task.user_id == user_id)

    # Apply completion filter if specified
    if completed is not None:
        base_query = base_query.where(Task.completed == completed)

    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    result = await session.execute(count_query)
    total = result.scalar_one()

    # Apply ordering, pagination
    query = (
        base_query
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await session.execute(query)
    tasks = list(result.scalars().all())

    return tasks, total


async def get_task_by_id(session: AsyncSession, task_id: int, user_id: str) -> Optional[Task]:
    """Get a single task by ID, ensuring it belongs to the user."""
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_task(session: AsyncSession, user_id: str, task_data: TaskCreate) -> Task:
    """Create a new task for a user."""
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=utc_now_naive(),
        updated_at=utc_now_naive(),
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task(
    session: AsyncSession,
    task: Task,
    task_data: TaskUpdate
) -> Task:
    """Update an existing task."""
    update_data = task_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = utc_now_naive()

    for field, value in update_data.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task: Task) -> None:
    """Delete a task."""
    await session.delete(task)
    await session.commit()


async def toggle_task_completion(session: AsyncSession, task: Task) -> Task:
    """Toggle the completion status of a task."""
    task.completed = not task.completed
    task.updated_at = utc_now_naive()

    await session.commit()
    await session.refresh(task)
    return task

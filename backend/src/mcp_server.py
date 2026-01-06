"""Official MCP Server for Task CRUD operations.

This server exposes task management tools to AI agents via the Model Context Protocol (MCP).
It acts as a bridge between the AI agent (Gemini 2.5 Flash) and the task database,
enabling natural language task operations while maintaining user isolation.

Architecture:
- Uses FastMCP for HTTP streaming transport
- User isolation via user_id query parameter in MCP server URL
- Synchronous database operations (psycopg2) for MCP tool compatibility
- Each tool call is scoped to the authenticated user_id

Tools exposed:
- create_task: Create a new task
- list_tasks: List user's tasks with optional filtering
- update_task: Update existing task fields
- complete_task: Toggle task completion status
- delete_task: Remove a task

Usage:
    # Run as standalone MCP server
    python -m src.mcp_server

    # The agent runner connects via MCPServerStreamableHttp:
    # MCPServerStreamableHttp(
    #     name="Todo MCP Server",
    #     params={"url": "http://localhost:8001?user_id=xxx"}
    # )
"""
import logging
import os
import sys
from typing import Optional, Dict, Any

# Configure logging for MCP server
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server")

# FastMCP imports
try:
    from fastmcp import FastMCP
    from fastmcp.server.dependencies import get_http_request
except ImportError as e:
    print(f"Error: FastMCP not installed. Run: pip install fastmcp", file=sys.stderr)
    raise

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Database imports - use synchronous engine for MCP tools
from sqlmodel import Session, create_engine, select
from sqlalchemy.pool import NullPool

from .models import Task
from .schemas.task import TaskCreate, TaskUpdate


def get_user_id_from_request() -> str:
    """Extract user_id from the HTTP request query parameters.

    This provides task isolation by getting the user_id from the MCP
    server URL, which is set by the agent runner for each user session.

    Returns:
        str: The user_id from query params

    Raises:
        ValueError: If user_id is not provided in the request
    """
    try:
        request = get_http_request()
        user_id = request.query_params.get("user_id")
        if not user_id:
            logger.error("No user_id provided in MCP request")
            raise ValueError("user_id is required for task operations")
        logger.debug(f"Extracted user_id from request: {user_id}")
        return user_id
    except RuntimeError as e:
        # get_http_request() raises RuntimeError if not in HTTP context
        logger.error(f"Failed to get HTTP request context: {e}")
        raise ValueError("Cannot determine user context - not in HTTP request")


# Create synchronous database engine for MCP server
# Convert asyncpg URL to psycopg2 URL for sync operations
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    # Replace asyncpg with psycopg2 for sync operations
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql://", 1)
    # Handle SSL mode
    if "?ssl=require" in SYNC_DATABASE_URL:
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("?ssl=require", "?sslmode=require")
    elif "&ssl=require" in SYNC_DATABASE_URL:
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("&ssl=require", "&sslmode=require")
    # Remove sslmode for psycopg2 if present (handle via connect_args)
    if "sslmode" in SYNC_DATABASE_URL:
        # Parse and remove sslmode, we'll handle it via connect_args
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(SYNC_DATABASE_URL)
        query_params = parse_qs(parsed.query)
        if "sslmode" in query_params:
            del query_params["sslmode"]
        new_query = urlencode(query_params, doseq=True)
        SYNC_DATABASE_URL = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
else:
    SYNC_DATABASE_URL = "postgresql://localhost/todoapp"

# Create sync engine with NullPool for serverless (Neon)
# Each request gets a fresh connection that's closed after use
try:
    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # Disable connection pooling for serverless
        connect_args={"sslmode": "require"} if "neon" in SYNC_DATABASE_URL else {},
    )
except Exception as e:
    logger.warning(f"Failed to create sync engine with SSL: {e}")
    # Fallback without SSL
    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

# Create FastMCP server instance
mcp = FastMCP("todo-task-server")


# MCP Tool Definitions
# Each tool corresponds to a task operation and includes comprehensive docstrings
# for LLM understanding.
# Note: user_id is automatically extracted from HTTP request query params


@mcp.tool
def create_task(
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new task for the current user.

    Creates a new todo task with the specified title and optional description.
    The task starts as incomplete by default.
    The user is automatically identified from the session context.

    Args:
        title: The task title (required, 1-200 characters)
        description: Optional detailed description (max 1000 characters)

    Returns:
        A dictionary containing the created task with fields:
        - status: "created"
        - task_id: Unique task identifier
        - title: Task title
        - description: Task details (may be null)
        - completed: False (newly created tasks are incomplete)
        - created_at: Creation timestamp
        - updated_at: Last modification timestamp

    Example:
        User: "Create a task to buy groceries"
        Agent: create_task(title="Buy groceries")

        User: "Add a task to finish the report by Friday with details"
        Agent: create_task(
            title="Finish report by Friday",
            description="Complete quarterly sales report and send to manager"
        )
    """
    try:
        # Get user_id from request context for task isolation
        user_id = get_user_id_from_request()

        with Session(sync_engine) as session:
            # Create task
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "created",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }
    except Exception as e:
        logger.error(f"Tool error in create_task: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool
def list_tasks(
    status: str = "all",
    limit: int = 100
) -> Dict[str, Any]:
    """List tasks for the current user with optional filtering.

    Retrieves the user's tasks, optionally filtered by completion status.
    Results are ordered by creation date (newest first) and paginated.
    The user is automatically identified from the session context.

    Args:
        status: Filter by "all", "pending", or "completed" (default: "all")
        limit: Maximum number of tasks to return (default 100, max 100)

    Returns:
        A dictionary containing:
        - tasks: List of task objects (each with id, title, description, completed, timestamps)
        - total: Total number of tasks matching the filter
        - count: Number of tasks returned in this response
        - pending_count: Number of incomplete tasks
        - completed_count: Number of completed tasks

    Example:
        User: "Show me all my tasks"
        Agent: list_tasks(status="all")

        User: "What tasks do I have left to do?"
        Agent: list_tasks(status="pending")

        User: "Show me completed tasks"
        Agent: list_tasks(status="completed")
    """
    try:
        # Get user_id from request context for task isolation
        user_id = get_user_id_from_request()

        with Session(sync_engine) as session:
            query = select(Task).where(Task.user_id == user_id)

            # Filter by status
            if status == "pending":
                query = query.where(Task.completed == False)  # noqa: E712
            elif status == "completed":
                query = query.where(Task.completed == True)  # noqa: E712

            # Order by creation date (newest first)
            query = query.order_by(Task.created_at.desc())

            # Apply limit
            query = query.limit(min(limit, 100))

            tasks = session.exec(query).all()

            # Count tasks by status
            pending_count = sum(1 for t in tasks if not t.completed)
            completed_count = sum(1 for t in tasks if t.completed)

            task_list = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                }
                for t in tasks
            ]

            return {
                "tasks": task_list,
                "total": len(task_list),
                "count": len(task_list),
                "pending_count": pending_count,
                "completed_count": completed_count,
            }
    except Exception as e:
        logger.error(f"Tool error in list_tasks: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """Update an existing task's fields.

    Updates one or more fields of an existing task. Only the specified fields
    are modified; unspecified fields remain unchanged. The user must own the task.
    The user is automatically identified from the session context.

    Args:
        task_id: The ID of the task to update
        title: New title (optional, 1-200 characters)
        description: New description (optional, max 1000 characters)
        completed: New completion status (optional, True/False)

    Returns:
        A dictionary containing the updated task with all current field values.

    Raises:
        Error if task not found or user doesn't own the task.

    Example:
        User: "Rename task 5 to 'Buy milk and eggs'"
        Agent: update_task(task_id=5, title="Buy milk and eggs")

        User: "Mark task 3 as done"
        Agent: update_task(task_id=3, completed=True)

        User: "Update the description of task 7"
        Agent: update_task(task_id=7, description="New details here")
    """
    try:
        # Get user_id from request context for task isolation
        user_id = get_user_id_from_request()

        with Session(sync_engine) as session:
            # Verify task exists and belongs to user
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "message": f"Task {task_id} not found or access denied"}

            # Update fields if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if completed is not None:
                task.completed = completed

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "status": "updated",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }
    except Exception as e:
        logger.error(f"Tool error in update_task: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool
def complete_task(
    task_id: int
) -> Dict[str, Any]:
    """Toggle the completion status of a task.

    Flips a task's completion status: incomplete -> complete or complete -> incomplete.
    This is the primary way users mark tasks as done or reopen completed tasks.
    The user is automatically identified from the session context.

    Args:
        task_id: The ID of the task to toggle

    Returns:
        A dictionary containing the updated task with the new completion status.

    Raises:
        Error if task not found or user doesn't own the task.

    Example:
        User: "Mark task 8 as complete"
        Agent: complete_task(task_id=8)

        User: "I finished the grocery task"
        Agent: First list tasks to find "grocery" task ID, then complete_task(task_id=X)

        User: "Reopen task 12"
        Agent: complete_task(task_id=12)  # Toggles back to incomplete
    """
    try:
        # Get user_id from request context for task isolation
        user_id = get_user_id_from_request()

        with Session(sync_engine) as session:
            # Verify task exists and belongs to user
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "message": f"Task {task_id} not found or access denied"}

            # Toggle completion status
            task.completed = not task.completed

            session.add(task)
            session.commit()
            session.refresh(task)

            status = "completed" if task.completed else "reopened"
            return {
                "status": status,
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }
    except Exception as e:
        logger.error(f"Tool error in complete_task: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool
def delete_task(
    task_id: int
) -> Dict[str, Any]:
    """Delete a task permanently.

    Removes a task from the database. This operation cannot be undone.
    The agent should confirm with the user before deleting tasks, especially for
    bulk deletions (multiple tasks at once).
    The user is automatically identified from the session context.

    Args:
        task_id: The ID of the task to delete

    Returns:
        A dictionary containing:
        - status: "deleted"
        - task_id: The ID of the deleted task
        - title: The title of the deleted task

    Raises:
        Error if task not found or user doesn't own the task.

    Example:
        User: "Delete task 15"
        Agent: delete_task(task_id=15)

        User: "Remove the grocery task"
        Agent: First list tasks to find "grocery" task ID, then delete_task(task_id=X)

        User: "Delete all completed tasks"
        Agent: Should confirm with user first, then delete each completed task ID
    """
    try:
        # Get user_id from request context for task isolation
        user_id = get_user_id_from_request()

        with Session(sync_engine) as session:
            # Verify task exists and belongs to user
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"status": "error", "message": f"Task {task_id} not found or access denied"}

            title = task.title
            session.delete(task)
            session.commit()

            return {
                "status": "deleted",
                "task_id": task_id,
                "title": title,
            }
    except Exception as e:
        logger.error(f"Tool error in delete_task: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# Export for importing from this module
mcp_server = mcp


def run_server() -> None:
    """Run the MCP server with HTTP transport and health endpoint."""
    import uvicorn
    from datetime import datetime
    from starlette.applications import Starlette
    from starlette.routing import Route, Mount
    from starlette.responses import JSONResponse

    # Get port from environment or use default
    port = int(os.environ.get("MCP_SERVER_PORT", "8001"))

    async def health_endpoint(request):
        """Health check endpoint for Docker/Kubernetes.

        Returns JSON with service status, name, and version.
        This endpoint is used by container orchestration for liveness/readiness probes.
        """
        return JSONResponse(
            {
                "status": "healthy",
                "service": "todo-mcp-server",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    # Create MCP app with Streamable HTTP transport
    # Required for OpenAI Agents SDK's MCPServerStreamableHttp client
    try:
        from fastmcp.server.http import create_streamable_http_app

        # Create Streamable HTTP app - single endpoint for requests/responses
        # Path "/" means endpoint is at mount point (/mcp)
        mcp_app = create_streamable_http_app(mcp, streamable_http_path="/")

        # IMPORTANT: Must pass lifespan from mcp_app to parent Starlette app
        # This initializes the StreamableHTTPSessionManager task group
        app = Starlette(
            routes=[
                Route("/health", health_endpoint, methods=["GET"]),
                Mount("/mcp", app=mcp_app),
            ],
            lifespan=mcp_app.lifespan,  # Required for FastMCP!
        )

        # Print startup info to stderr (same as uvicorn) to ensure visibility
        import sys
        print(f"\n{'='*60}", file=sys.stderr, flush=True)
        print(f"🚀 Todo MCP Server starting on http://0.0.0.0:{port}", file=sys.stderr, flush=True)
        print(f"📦 Database: {SYNC_DATABASE_URL[:50]}..." if len(SYNC_DATABASE_URL) > 50 else f"📦 Database: {SYNC_DATABASE_URL}", file=sys.stderr, flush=True)
        print("🔧 Available tools:", file=sys.stderr, flush=True)
        print("   Tasks: create_task, list_tasks, update_task, complete_task, delete_task", file=sys.stderr, flush=True)
        print(f"🏥 Health: http://0.0.0.0:{port}/health", file=sys.stderr, flush=True)
        print(f"🔌 MCP endpoint: http://0.0.0.0:{port}/mcp (Streamable HTTP)", file=sys.stderr, flush=True)
        print(f"{'='*60}\n", file=sys.stderr, flush=True)

        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

    except ImportError as e:
        # Fallback to mcp.run() with streamable-http transport
        import sys
        logger.warning(f"create_streamable_http_app not available ({e}), using mcp.run()")

        print(f"\n{'='*60}", file=sys.stderr, flush=True)
        print(f"🚀 Todo MCP Server (fallback) on http://0.0.0.0:{port}", file=sys.stderr, flush=True)
        print(f"📦 Database: {SYNC_DATABASE_URL[:50]}..." if len(SYNC_DATABASE_URL) > 50 else f"📦 Database: {SYNC_DATABASE_URL}", file=sys.stderr, flush=True)
        print("🔧 Available tools:", file=sys.stderr, flush=True)
        print("   Tasks: create_task, list_tasks, update_task, complete_task, delete_task", file=sys.stderr, flush=True)
        print("⚠️  Health check: Configure at ingress/proxy level", file=sys.stderr, flush=True)
        print(f"{'='*60}\n", file=sys.stderr, flush=True)

        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=port,
        )


# Module entry point
if __name__ == "__main__":
    run_server()

"""
Example usage of the AI Agent configuration.

This file demonstrates how to use the agent module in FastAPI routes
for the chatbot feature.

DO NOT import this in production code - it's for reference only.
"""

import asyncio
from typing import List

from agent import get_llm_client
from agent.config import get_agent_config, get_model_info, get_rate_limiter_config


async def example_simple_chat():
    """Simple example: Send a message to Gemini."""
    print("\n=== Example 1: Simple Chat ===")

    client = get_llm_client()

    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a helpful task management assistant."},
            {"role": "user", "content": "Add a task to buy groceries"},
        ],
        temperature=0.7,
        max_tokens=200,
    )

    print(f"Assistant: {response.choices[0].message.content}")
    print(f"Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")


async def example_conversation_with_history():
    """Example with conversation history (sliding window)."""
    print("\n=== Example 2: Conversation with History ===")

    config = get_agent_config()
    client = get_llm_client()

    # Simulated conversation history from database
    conversation_history = [
        {"role": "system", "content": "You are a task assistant. Help users manage their todos."},
        {"role": "user", "content": "Add a task to call mom"},
        {"role": "assistant", "content": "Task added: Call mom (ID: 42)"},
        {"role": "user", "content": "What tasks do I have?"},
        {"role": "assistant", "content": "You have 1 task:\n1. Call mom (pending)"},
    ]

    # Add new user message
    conversation_history.append({"role": "user", "content": "Mark task 42 as done"})

    # Sliding window: only send last N messages
    max_messages = config.max_context_messages
    windowed_history = conversation_history[-max_messages:]

    response = await client.chat.completions.create(
        model=config.gemini_model,
        messages=windowed_history,
        temperature=0.7,
    )

    print(f"User: Mark task 42 as done")
    print(f"Assistant: {response.choices[0].message.content}")
    print(f"Context window size: {len(windowed_history)} messages")


async def example_with_function_calling():
    """Example showing how to structure for MCP tool integration."""
    print("\n=== Example 3: Function Calling Pattern (MCP Tools) ===")

    client = get_llm_client()

    # This is the pattern we'll use when integrating with FastMCP
    # The actual tool definitions will come from the MCP server
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task to the user's todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title or description",
                        },
                        "description": {
                            "type": "string",
                            "description": "Additional details about the task",
                        },
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status",
                        }
                    },
                },
            },
        },
    ]

    messages = [
        {"role": "system", "content": "You help users manage tasks. Call appropriate functions."},
        {"role": "user", "content": "Add a task to prepare presentation"},
    ]

    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    if message.tool_calls:
        print(f"Function to call: {message.tool_calls[0].function.name}")
        print(f"Arguments: {message.tool_calls[0].function.arguments}")
    else:
        print(f"Response: {message.content}")


def example_configuration_inspection():
    """Show how to inspect configuration at runtime."""
    print("\n=== Example 4: Configuration Inspection ===")

    # Get configuration
    config = get_agent_config()
    print(f"Model: {config.gemini_model}")
    print(f"Rate limit: {config.rate_limit_per_minute} req/min")
    print(f"Context window: {config.max_context_messages} messages")
    print(f"Timeout: {config.llm_timeout_seconds}s")

    # Get model info
    info = get_model_info()
    print(f"\nModel Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Get rate limiter config
    rate_config = get_rate_limiter_config()
    print(f"\nRate Limiter:")
    for key, value in rate_config.items():
        print(f"  {key}: {value}")


async def example_error_handling():
    """Show proper error handling patterns."""
    print("\n=== Example 5: Error Handling ===")

    client = get_llm_client()

    try:
        response = await client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "user", "content": "Hello!"},
            ],
            max_tokens=10,
        )
        print(f"Success: {response.choices[0].message.content}")

    except asyncio.TimeoutError:
        print("Error: Request timed out")
        # Return error to user: "Assistant is taking too long, please try again"

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        # Log error and return friendly message to user
        # "Sorry, I'm having trouble right now. Please try again."


async def main():
    """Run all examples."""
    print("=" * 60)
    print("AI Agent Configuration Examples")
    print("=" * 60)

    # Configuration inspection (sync)
    example_configuration_inspection()

    # Note: The actual chat examples require a valid GEMINI_API_KEY
    # Uncomment below when running with real credentials:

    # await example_simple_chat()
    # await example_conversation_with_history()
    # await example_with_function_calling()
    # await example_error_handling()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    # This demonstrates how to run async code
    asyncio.run(main())

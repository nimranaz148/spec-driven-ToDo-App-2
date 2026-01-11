def format_ai_prompt(prompt):
    """
    Formats a natural language prompt for kubectl-ai.
    """
    return f"kubectl-ai: {prompt}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(format_ai_prompt(sys.argv[1]))
    else:
        print("Usage: python helper.py <prompt>")

def kagent_status_map(status):
    """
    Maps simplified status to kagent commands.
    """
    mapping = {
        "health": "kagent report --health",
        "cost": "kagent analyze --cost",
        "security": "kagent scan --security"
    }
    return mapping.get(status, "kagent help")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(kagent_status_map(sys.argv[1]))
    else:
        print("Usage: python helper.py <status_type>")

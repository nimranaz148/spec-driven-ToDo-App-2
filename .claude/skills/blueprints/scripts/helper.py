def analyze_blueprint_request(spec_content):
    """
    Analyzes a spec content to recommend a blueprint pattern.
    """
    if "database" in spec_content.lower() or "persistent" in spec_content.lower():
        return "Stateful Service Pattern"
    elif "cron" in spec_content.lower() or "schedule" in spec_content.lower():
        return "CronJob Pattern"
    elif "run once" in spec_content.lower():
        return "Job Pattern"
    else:
        return "Stateless Service Pattern"

if __name__ == "__main__":
    import sys
    # Simple CLI for testing
    if len(sys.argv) > 1:
        print(analyze_blueprint_request(sys.argv[1]))
    else:
        print("Usage: python helper.py <spec_content>")

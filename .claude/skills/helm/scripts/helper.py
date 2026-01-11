def helm_template_structure(name):
    """
    Returns the basic structure of a Helm chart.
    """
    return {
        name: [
            "Chart.yaml",
            "values.yaml",
            "templates/",
            "templates/deployment.yaml",
            "templates/service.yaml",
            "templates/_helpers.tpl"
        ]
    }

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        print(json.dumps(helm_template_structure(sys.argv[1]), indent=2))
    else:
        print("Usage: python helper.py <chart_name>")

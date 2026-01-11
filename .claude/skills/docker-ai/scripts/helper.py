def get_docker_template(lang):
    """
    Returns a basic Dockerfile template for the specified language.
    """
    templates = {
        "python": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]""",
        "node": """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "start"]"""
    }
    return templates.get(lang, "# Unknown language")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(get_docker_template(sys.argv[1]))
    else:
        print("Usage: python helper.py <language>")

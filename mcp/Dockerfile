# Build from repository root with: docker build -f mcp/Dockerfile -t mcp:latest .
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/README.md ./
RUN pip install --no-cache-dir -e .
COPY backend/src/ ./src/

# Stage 2: Runtime
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app ./

USER appuser
EXPOSE 8001
CMD ["python", "-m", "src.mcp_server"]

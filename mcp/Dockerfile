# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e .
COPY backend/src/ ./src/

# Stage 2: Runtime
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder /app ./
USER appuser
EXPOSE 8001
CMD ["python", "-m", "src.mcp_server"]

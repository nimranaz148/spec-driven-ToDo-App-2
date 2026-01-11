# Docker AI Reference

## Command Reference

### Docker AI (Gordon)
If available, use `docker ai` command:
- `docker ai "how do Iize this app?"`
- `docker ai "optimize this Dockerfile"`

### Claude Code Simulation
If Gordon is unavailable, use Claude Code to simulate:
- `@skill:docker-ai optimize Dockerfile`
- `@skill:docker-ai explain build error`

## Best Practices
1. **Multi-stage builds**: Always use multi-stage builds for smaller images.
2. **Layer caching**: Order Dockerfile instructions to maximize cache hits.
3. **Non-root user**: Run containers as non-root user for security.
4. **Healthchecks**: Include HEALTHCHECK instruction.

# Kubernetes Deployment Script for Windows PowerShell
# Run this script to deploy the Todo App to Minikube

Write-Host "Starting Todo App Deployment to Minikube..." -ForegroundColor Green

# Step 1: Configure Docker to use Minikube
Write-Host "`n[1/5] Configuring Docker for Minikube..." -ForegroundColor Cyan
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Step 2: Build Docker Images
Write-Host "`n[2/5] Building Docker images (this may take 5-10 minutes)..." -ForegroundColor Cyan

Write-Host "  Building frontend..." -ForegroundColor Yellow
docker build -t frontend:latest ./frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Frontend build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Frontend built successfully" -ForegroundColor Green

Write-Host "  Building backend..." -ForegroundColor Yellow
docker build -t backend:latest ./backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Backend build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Backend built successfully" -ForegroundColor Green

Write-Host "  Building MCP server..." -ForegroundColor Yellow
docker build -t mcp:latest ./mcp
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ MCP build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ MCP built successfully" -ForegroundColor Green

# Step 3: Verify images
Write-Host "`n[3/5] Verifying built images..." -ForegroundColor Cyan
docker images | Select-String "frontend|backend|mcp"

# Step 4: Deploy with Helm
Write-Host "`n[4/5] Deploying with Helm..." -ForegroundColor Cyan

# Check if environment variables are set
if (-not $env:DATABASE_URL) {
    Write-Host "  ❌ ERROR: DATABASE_URL not set!" -ForegroundColor Red
    Write-Host "  Run: `$env:DATABASE_URL='your-database-url'" -ForegroundColor Yellow
    exit 1
}

if (-not $env:GEMINI_API_KEY -and -not $env:OPENAI_API_KEY) {
    Write-Host "  ❌ ERROR: GEMINI_API_KEY or OPENAI_API_KEY not set!" -ForegroundColor Red
    Write-Host "  Run: `$env:GEMINI_API_KEY='your-api-key'" -ForegroundColor Yellow
    exit 1
}

# Use GEMINI_API_KEY if available, otherwise OPENAI_API_KEY
$API_KEY = if ($env:GEMINI_API_KEY) { $env:GEMINI_API_KEY } else { $env:OPENAI_API_KEY }

# Set default BETTER_AUTH_SECRET if not provided
if (-not $env:BETTER_AUTH_SECRET) {
    $env:BETTER_AUTH_SECRET = "default-secret-change-in-production"
    Write-Host "  ⚠️  Using default BETTER_AUTH_SECRET" -ForegroundColor Yellow
}

Write-Host "  Installing Helm chart..." -ForegroundColor Yellow
helm install todo-app ./helm/todo-app `
    --namespace todo-app `
    --create-namespace `
    --set secrets.databaseUrl="$env:DATABASE_URL" `
    --set secrets.openaiApiKey="$API_KEY" `
    --set secrets.betterAuthSecret="$env:BETTER_AUTH_SECRET"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Helm deployment failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Helm chart deployed successfully" -ForegroundColor Green

# Step 5: Wait for pods to be ready
Write-Host "`n[5/5] Waiting for pods to be ready (this may take 2-3 minutes)..." -ForegroundColor Cyan
kubectl wait --for=condition=ready pod -l app=todo-chatbot -n todo-app --timeout=300s

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "`nPod status:" -ForegroundColor Cyan
    kubectl get pods -n todo-app
    
    Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Add to hosts file (as Administrator):"
    Write-Host "     Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value '127.0.0.1 todo.local'"
    Write-Host "`n  2. Start Minikube tunnel (in a separate PowerShell window):"
    Write-Host "     minikube tunnel"
    Write-Host "`n  3. Access the application:"
    Write-Host "     http://todo.local"
} else {
    Write-Host "`n❌ Pod deployment timed out or failed!" -ForegroundColor Red
    Write-Host "Check pod status with: kubectl get pods -n todo-app" -ForegroundColor Yellow
    Write-Host "Check logs with: kubectl logs -n todo-app -l app=todo-chatbot" -ForegroundColor Yellow
}

# 🐳 Docker Deployment Guide

## Quick Deploy

### Windows:
```cmd
.\deploy.bat
```

### Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Manual Deployment

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your Discord webhook URL
nano .env
```

### 2. Build Image
```bash
docker build -t nifty-arbitrage-scanner .
```

### 3. Run Container
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or using docker directly
docker run -d \
  --name nifty-arbitrage-scanner \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  nifty-arbitrage-scanner
```

## Container Management

### View Logs
```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Stop/Start
```bash
# Stop container
docker-compose down

# Start container
docker-compose up -d

# Restart container
docker-compose restart
```

### Update Container
```bash
# Rebuild and restart
docker-compose down
docker build -t nifty-arbitrage-scanner .
docker-compose up -d
```

## Server Deployment

### VPS Setup (Ubuntu)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Clone your repository
git clone https://github.com/yourusername/nifty_listing_scraper.git
cd nifty_listing_scraper

# Setup environment
cp .env.example .env
nano .env  # Add your Discord webhook URL

# Deploy
chmod +x deploy.sh
./deploy.sh
```

### 24/7 Monitoring
The container is configured with:
- **Auto-restart**: Restarts if it crashes
- **Health checks**: Monitors container health
- **Resource limits**: 1GB memory limit
- **Log rotation**: Prevents disk space issues

### Performance Optimization
- **Headless mode**: Reduces memory usage
- **Resource limits**: Prevents server overload  
- **Scan intervals**: Configurable via environment variables
- **Efficient logging**: Structured logs with rotation

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | - | ✅ Yes |
| `SCAN_INTERVAL` | Seconds between scans | 300 | No |
| `MAX_ITEMS` | Max items per scan (0=unlimited) | 0 | No |
| `MAX_SCROLLS` | Max scroll attempts | 400 | No |

## Troubleshooting

### Container won't start:
```bash
# Check logs
docker-compose logs

# Check container status
docker-compose ps
```

### Discord notifications not working:
```bash
# Test webhook manually
curl -X POST -H "Content-Type: application/json" \
  -d '{"content": "Test from Docker container"}' \
  $DISCORD_WEBHOOK_URL
```

### ChromeDriver compatibility issues:
```bash
# If you get ChromeDriver errors, rebuild with:
docker build --no-cache -t nifty-arbitrage-scanner .

# Check Chrome and ChromeDriver versions in container:
docker run --rm nifty-arbitrage-scanner google-chrome --version
docker run --rm nifty-arbitrage-scanner chromedriver --version
```

### High memory usage:
- Reduce `MAX_ITEMS` and `MAX_SCROLLS`
- Increase `SCAN_INTERVAL`
- Monitor with `docker stats`

### Update code:
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker build -t nifty-arbitrage-scanner .
docker-compose up -d
```

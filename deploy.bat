@echo off
echo 🚀 Building Nifty Arbitrage Scanner Docker image...

:: Build the image
docker build -t nifty-arbitrage-scanner .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Docker image built successfully!
    
    :: Check if .env file exists
    if not exist ".env" (
        echo ⚠️  .env file not found. Creating from template...
        copy .env.example .env
        echo 📝 Please edit .env file with your Discord webhook URL before running.
        pause
        exit /b 1
    )
    
    echo 🔄 Starting container with docker-compose...
    docker-compose up -d
    
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Container started successfully!
        echo 📊 View logs with: docker-compose logs -f
        echo 🛑 Stop with: docker-compose down
        echo 🔍 Check status: docker-compose ps
    ) else (
        echo ❌ Failed to start container
        pause
        exit /b 1
    )
) else (
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

pause

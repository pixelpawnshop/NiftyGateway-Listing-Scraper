#!/bin/bash

# Build and deploy the arbitrage scanner
echo "🚀 Building Nifty Arbitrage Scanner Docker image..."

# Build the image
docker build -t nifty-arbitrage-scanner .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found. Creating from template..."
        cp .env.example .env
        echo "📝 Please edit .env file with your Discord webhook URL before running."
        exit 1
    fi
    
    echo "🔄 Starting container with docker-compose..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "📊 View logs with: docker-compose logs -f"
        echo "🛑 Stop with: docker-compose down"
        echo "🔍 Check status: docker-compose ps"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

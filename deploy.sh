#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting deployment of AI Trading Lab..."

echo "📥 Pulling latest code from GitHub (main branch)..."
git pull origin main

echo "🛑 Stopping currently running containers..."
docker-compose down

echo "🔨 Building new Docker images with the latest code..."
docker-compose build

echo "✅ Starting containers in the background..."
docker-compose up -d

echo "🧹 Cleaning up old unused Docker images to save disk space..."
docker image prune -f

echo "🎉 Deployment complete! The lab is now running on the latest commit."
echo "👉 You can view the live logs anytime by running: docker-compose logs -f"

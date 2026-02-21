#!/bin/bash

# Reddit SaaS Validator - Deployment Commands
# Run after creating GitHub repository

echo "🚀 Starting deployment process..."
echo ""

# Step 1: Set GitHub remote
echo "Step 1: Setting GitHub remote..."
echo "Replace YOUR_USERNAME with your GitHub username:"
echo "git remote set-url origin https://github.com/YOUR_USERNAME/reddit-saas-validator.git"
echo ""
read -p "Press Enter after you've run the command above..."

# Step 2: Push to GitHub
echo ""
echo "Step 2: Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Code pushed to GitHub successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Deploy backend on Railway: https://railway.app"
    echo "2. Deploy frontend on Vercel: https://vercel.com"
    echo ""
    echo "📖 Follow the guide: DEPLOY_NOW.md"
else
    echo ""
    echo "❌ Push failed. Make sure you:"
    echo "1. Created GitHub repository"
    echo "2. Updated remote URL with correct username"
    echo "3. Have GitHub access configured"
fi

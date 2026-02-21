#!/bin/bash
# Quick script to push to GitHub

echo "🚀 Reddit SaaS Validator - GitHub Push Script"
echo "=============================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository!"
    exit 1
fi

# Check for existing remote
if git remote | grep -q "origin"; then
    echo "ℹ️  Remote 'origin' already exists:"
    git remote get-url origin
    echo ""
    read -p "Remove and reconfigure? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        git remote remove origin
    else
        echo "Keeping existing remote."
        exit 0
    fi
fi

# Get GitHub username
echo ""
echo "📝 Enter your GitHub username:"
read -p "Username: " github_user

if [ -z "$github_user" ]; then
    echo "❌ Username cannot be empty!"
    exit 1
fi

# Construct repository URL
repo_url="https://github.com/$github_user/reddit-saas-validator.git"

echo ""
echo "🔗 Will add remote:"
echo "   $repo_url"
echo ""

# Confirm
read -p "Continue? (Y/n): " confirm
if [[ $confirm == [nN] ]]; then
    echo "Cancelled."
    exit 0
fi

# Add remote
echo ""
echo "Adding remote..."
git remote add origin "$repo_url"

if [ $? -eq 0 ]; then
    echo "✅ Remote added successfully!"
else
    echo "❌ Failed to add remote!"
    exit 1
fi

echo ""
echo "Current remotes:"
git remote -v

echo ""
echo "📤 Ready to push!"
echo ""
read -p "Push to GitHub now? (Y/n): " push_confirm

if [[ $push_confirm != [nN] ]]; then
    echo ""
    echo "Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully pushed to GitHub!"
        echo ""
        echo "🎉 Your project is now live at:"
        echo "   https://github.com/$github_user/reddit-saas-validator"
        echo ""
        echo "📋 Next steps:"
        echo "   1. Visit your repo and verify all files"
        echo "   2. Add topics: saas, validation, reddit, twitter, linkedin"
        echo "   3. Create release v1.0.0"
        echo "   4. Share on social media!"
        echo ""
        echo "📄 See GITHUB_PUSH_NOW.md for detailed post-push steps."
    else
        echo ""
        echo "❌ Push failed!"
        echo ""
        echo "Common issues:"
        echo "  1. Repository doesn't exist on GitHub yet"
        echo "     → Create it first: https://github.com/new"
        echo "  2. Authentication failed"
        echo "     → Use Personal Access Token or SSH"
        echo "  3. Wrong repository name/username"
        echo ""
        echo "Manual push:"
        echo "  git push -u origin main"
    fi
else
    echo ""
    echo "Manual push command:"
    echo "  git push -u origin main"
fi

echo ""
echo "✅ Done!"

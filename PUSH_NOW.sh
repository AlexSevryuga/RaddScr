#!/bin/bash
# Push to GitHub (repository must exist first!)

cd /Users/aleksej/clawd/reddit-saas-validator

echo "🚀 Pushing to GitHub..."
echo ""
echo "Repository: https://github.com/AlexSevryuga/reddit-saas-validator"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🎉 Your project is now live at:"
    echo "   https://github.com/AlexSevryuga/reddit-saas-validator"
    echo ""
    echo "📋 Next steps:"
    echo ""
    echo "1. Add topics (Settings → Topics):"
    echo "   saas, validation, reddit, twitter, linkedin, python, market-research"
    echo ""
    echo "2. Set website URL (Settings → General):"
    echo "   https://reddit-saas-validator.vercel.app"
    echo ""
    echo "3. Create first release:"
    echo "   - Go to Releases → Create a new release"
    echo "   - Tag: v1.0.0"
    echo "   - Title: 🚀 v1.0.0 - Initial Release"
    echo "   - Copy notes from CHANGELOG.md"
    echo ""
    echo "4. Share on social media!"
    echo "   - See GITHUB_PUSH_NOW.md for templates"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Make sure you created the repository first:"
    echo "   https://github.com/new"
    echo ""
    echo "Repository name: reddit-saas-validator"
    echo "Visibility: Public"
    echo "Don't initialize with README, .gitignore or license"
    echo ""
fi

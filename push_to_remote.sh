#!/bin/bash
# Push script for Secure Home-Lab Setup
# This script will push the changes to the correct repository when configured

echo "🚀 Pushing Secure Home-Lab Setup to remote repository"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📌 Current branch: $CURRENT_BRANCH"

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    git status --short
    echo ""
    read -p "Do you want to commit these changes? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
    fi
fi

# Get repository URL
if [ -z "$1" ]; then
    echo "❓ No repository URL provided"
    echo "Usage: ./push_to_remote.sh <repository-url>"
    echo "Example: ./push_to_remote.sh https://github.com/username/Paradelala.git"
    exit 1
fi

REPO_URL=$1

# Set remote origin
echo "🔗 Setting remote origin to: $REPO_URL"
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

# Push to remote
echo "📤 Pushing to remote..."
if [ -n "$GITHUB_TOKEN" ]; then
    # Use token if available
    REPO_WITH_TOKEN=$(echo $REPO_URL | sed "s|https://|https://$GITHUB_TOKEN@|")
    git push -u "$REPO_WITH_TOKEN" "$CURRENT_BRANCH"
else
    git push -u origin "$CURRENT_BRANCH"
fi

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to remote!"
    echo "🌐 Branch '$CURRENT_BRANCH' is now available on the remote repository"
else
    echo "❌ Failed to push to remote"
    echo "Please check your repository URL and permissions"
fi

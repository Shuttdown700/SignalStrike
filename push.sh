#!/bin/bash

# Navigate to your git repository directory
# cd /path/to/your/repository

# Add all changes to the staging area
git add .

# Prompt user to enter a commit message
echo "Enter your commit message:"
read commit_message

# Commit changes with the user-provided message
git commit -m "$commit_message"

# Push changes to the 'main' branch of the remote repository
git push origin main
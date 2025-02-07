# Add all changes to Git
git add .

# Check if there are any changes
$changes = git status --porcelain
if ($changes) {
    # If there are changes, commit and push
    git commit -m "Deploy update"
    git push
}

# Deploy to Vercel
vercel deploy --prod 
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $PWD
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Debounce timer to prevent multiple commits for the same change
$script:lastRun = [DateTime]::MinValue
$debounceSeconds = 5

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $timeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Skip if the change is in .git directory or node_modules
    if ($path -match "\\\.git\\" -or $path -match "\\node_modules\\") {
        return
    }
    
    # Implement debouncing
    $now = Get-Date
    if (($now - $script:lastRun).TotalSeconds -lt $debounceSeconds) {
        return
    }
    $script:lastRun = $now
    
    Write-Host "Change detected in $path at $timeStamp"
    
    # Wait a brief moment to ensure file writing is complete
    Start-Sleep -Seconds 2
    
    try {
        # Check if there are any changes to commit
        $status = git status --porcelain
        if ($status) {
            # Remove any existing index.lock file
            $lockFile = Join-Path (git rev-parse --git-dir) "index.lock"
            if (Test-Path $lockFile) {
                Remove-Item $lockFile -Force
            }
            
            # Stage and commit changes
            git add .
            git commit -m "Auto-commit: Changes detected at $timeStamp"
            
            # Push changes
            git push origin master
            Write-Host "Successfully pushed changes at $timeStamp"
        }
    }
    catch {
        Write-Host "Error occurred: $_"
    }
}

# Register events
$handlers = . {
    Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action
}

Write-Host "Watching for changes in $($watcher.Path)"
Write-Host "Press Ctrl+C to stop"

try {
    while ($true) { Start-Sleep -Seconds 1 }
}
finally {
    $handlers | ForEach-Object {
        Unregister-Event -SourceIdentifier $_.Name
    }
    $watcher.Dispose()
    Write-Host "File watching stopped."
} 
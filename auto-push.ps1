$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $PWD
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $timeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host "Change detected in $path at $timeStamp"
    
    # Wait a brief moment to ensure file writing is complete
    Start-Sleep -Seconds 2
    
    # Run git commands
    git add .
    git commit -m "Auto-commit: File changes detected at $timeStamp"
    git push
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
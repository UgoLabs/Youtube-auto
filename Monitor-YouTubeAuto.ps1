# filepath: /c:/Users/okwum/youtube_auto/Monitor-YouTubeAuto.ps1

[CmdletBinding()]
param(
    [Parameter()]
    [string]$KeyPath = "C:\Users\okwum\Downloads\Youtube-auto.pem",
    
    [Parameter()]
    [string]$EC2IP = "3.139.86.85"
)

# Configuration
$config = @{
    KeyPath = $KeyPath
    EC2IP = $EC2IP
    ServiceName = "youtube_auto"
    DataDir = "/mnt/data/youtube_auto"
}

# SSH command builder
$sshCmd = "ssh -i `"$($config.KeyPath)`" ubuntu@$($config.EC2IP)"

# Function definitions
function Show-Header {
    Clear-Host
    Write-Host "YouTube Auto Service Monitor" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "Instance: $($config.EC2IP)"
    Write-Host "Service: $($config.ServiceName)`n"
}

function Show-Menu {
    Write-Host "1. View service status"
    Write-Host "2. Watch logs (live)"
    Write-Host "3. Check disk space"
    Write-Host "4. Restart service"
    Write-Host "5. Clean old files"
    Write-Host "6. Exit`n"
    
    $choice = Read-Host "Select option (1-6)"
    return $choice
}

function View-ServiceStatus {
    Write-Host "`nChecking service status..." -ForegroundColor Yellow
    Invoke-Expression "$sshCmd 'sudo systemctl status $($config.ServiceName)'"
    pause
}

function Watch-Logs {
    Write-Host "`nWatching logs (Ctrl+C to stop)..." -ForegroundColor Yellow
    Invoke-Expression "$sshCmd 'sudo journalctl -u $($config.ServiceName) -f'"
}

function Check-DiskSpace {
    Write-Host "`nChecking disk space..." -ForegroundColor Yellow
    Invoke-Expression "$sshCmd 'df -h $($config.DataDir)'"
    pause
}

function Restart-Service {
    Write-Host "`nRestarting service..." -ForegroundColor Yellow
    Invoke-Expression "$sshCmd 'sudo systemctl restart $($config.ServiceName)'"
    Start-Sleep -Seconds 2
    View-ServiceStatus
}

function Clean-OldFiles {
    Write-Host "`nCleaning old files..." -ForegroundColor Yellow
    $cleanup_commands = @(
        "find $($config.DataDir)/output -type f -mtime +7 -delete",
        "find $($config.DataDir)/logs -type f -mtime +30 -delete"
    )
    
    foreach ($cmd in $cleanup_commands) {
        Write-Host "Running: $cmd" -ForegroundColor Gray
        Invoke-Expression "$sshCmd '$cmd'"
    }
    
    Check-DiskSpace
}

# Main execution loop
try {
    do {
        Show-Header
        $choice = Show-Menu
        
        switch ($choice) {
            "1" { View-ServiceStatus }
            "2" { Watch-Logs }
            "3" { Check-DiskSpace }
            "4" { Restart-Service }
            "5" { Clean-OldFiles }
            "6" { exit }
            default { 
                Write-Host "`nInvalid option!" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    } while ($true)
} catch {
    Write-Host "`nError: $_" -ForegroundColor Red
    exit 1
}

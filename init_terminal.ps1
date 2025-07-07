# Terminal Initialization Script
# Run this script to initialize terminal for Cursor sessions

Write-Host "Initializing terminal for Cursor..." -ForegroundColor Yellow

# Load profile
. $PROFILE

# Clear any pending input
$Host.UI.RawUI.FlushInputBuffer()

# Set up environment
$env:TERM = "xterm-256color"
$env:COLORTERM = "truecolor"

# Configure PSReadLine
try {
    Import-Module PSReadLine -ErrorAction SilentlyContinue
    Set-PSReadLineOption -BellStyle None -ErrorAction SilentlyContinue
    Set-PSReadLineOption -EditMode Windows -ErrorAction SilentlyContinue
} catch {
    Write-Host "PSReadLine not available, continuing..." -ForegroundColor Yellow
}

# Set prompt function
function global:prompt {
    $Host.UI.RawUI.FlushInputBuffer()
    $Host.UI.RawUI.WindowTitle = "PowerShell - Ready"
    return "PS $($executionContext.SessionState.Path.CurrentLocation)> "
}

# Clear screen
Clear-Host

Write-Host "Terminal initialized successfully!" -ForegroundColor Green
Write-Host "Commands should complete without waiting." -ForegroundColor Green 
# Terminal Fix Script
# This script fixes the PowerShell waiting issue

Write-Host "Fixing terminal behavior..." -ForegroundColor Yellow

# Clear any pending input
$Host.UI.RawUI.FlushInputBuffer()

# Set a simple, responsive prompt
function global:prompt {
    $Host.UI.RawUI.WindowTitle = "PowerShell - Ready"
    return "PS $($executionContext.SessionState.Path.CurrentLocation)> "
}

# Disable bell if possible
try {
    Set-PSReadLineOption -BellStyle None -ErrorAction SilentlyContinue
} catch {
    # Ignore if not supported
}

# Clear the screen
Clear-Host

Write-Host "Terminal fixed! Commands should complete without waiting." -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Cyan

# Wait for user input to continue
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
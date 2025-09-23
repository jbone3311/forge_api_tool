# PowerShell script to install/update all core MCP servers globally
# Usage: Run in an elevated (Administrator) PowerShell terminal

$ErrorActionPreference = 'Stop'

$servers = @(
    'mcp-memory-bank',
    'mcp-knowledge-graph',
    '@YassineTk/mcp-docs-provider',
    '@modelcontextprotocol/server-sequential-thinking'
)

Write-Host "Installing/updating core MCP servers globally..." -ForegroundColor Cyan

foreach ($server in $servers) {
    Write-Host "\n--- Installing/updating $server ---" -ForegroundColor Yellow
    npm install -g $server
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully installed/updated $server." -ForegroundColor Green
    } else {
        Write-Host "Failed to install $server. Check npm logs for details." -ForegroundColor Red
    }
}

Write-Host "\nVerifying MCP server installations..." -ForegroundColor Cyan

# Print versions
$mcpCommands = @{
    'mcp-memory-bank' = 'mcp-memory-bank --version'
    'mcp-knowledge-graph' = 'mcp-knowledge-graph --help'
    '@YassineTk/mcp-docs-provider' = 'mcp-docs-provider --help'
    '@modelcontextprotocol/server-sequential-thinking' = 'server-sequential-thinking --help'
}

foreach ($server in $servers) {
    $cmd = $mcpCommands[$server]
    Write-Host "\n$server version/info:" -ForegroundColor Yellow
    try {
        iex $cmd
    } catch {
        Write-Host "Could not get version/info for $server." -ForegroundColor Red
    }
}

Write-Host "\nAll MCP servers processed. If any failed, please check your npm and PATH settings." -ForegroundColor Cyan 
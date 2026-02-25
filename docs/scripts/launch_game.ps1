# DBForged Launch Script
# Run this in PowerShell to start the game

# Add Node.js to PATH
$env:PATH = "C:\Program Files\nodejs;$env:PATH"

# Navigate to game directory
Set-Location "C:\Games\Dev\DBForged\Agents\MiniMax\DBForged"

# Start Evennia server
Write-Host "Starting Evennia server..." -ForegroundColor Cyan
python -m evennia start

# Wait a moment
Start-Sleep -Seconds 2

# Start web client
Write-Host "Starting web client..." -ForegroundColor Cyan
Set-Location "C:\Games\Dev\DBForged\Agents\MiniMax\DBForged\web\client"
npm run dev

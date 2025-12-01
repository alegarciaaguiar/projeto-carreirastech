# Run Gemini-enabled Flask app without saving the API key in the repo.
# This script prompts for the API key, sets the environment variable for this session,
# and launches the app. The key is not stored on disk by this script.

param()

Write-Host "Enter your Google Gemini API key (it will not be saved):"
$apiKey = Read-Host

if (-not $apiKey) {
    Write-Host "No key provided. Exiting." -ForegroundColor Yellow
    exit 1
}

# Set for current PowerShell session
$env:GOOGLE_API_KEY = $apiKey

Write-Host "Starting Flask app with GOOGLE_API_KEY set for this session..."
python projeto.py

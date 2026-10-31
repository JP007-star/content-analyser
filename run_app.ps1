<#
.SYNOPSIS
    Launch Content Analyser - Choose which app to run
#>

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  🔱 Content Analyser - JP Cinematic Universe" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Select app to run:"
Write-Host "  1. Main App (Both Analyzers)" -ForegroundColor Green
Write-Host "  2. YouTube Channel Analyzer (API-based)" -ForegroundColor Yellow
Write-Host "  3. YouTube Analyzer (Skills & Tools)" -ForegroundColor Magenta
Write-Host ""

$choice = Read-Host "Enter choice (1-3) [default=1]"
if (-not $choice) { $choice = "1" }

Set-Location $PSScriptRoot

switch ($choice) {
    "1" {
        Write-Host "Starting Main App at http://localhost:8501" -ForegroundColor Green
        streamlit run main_app.py --server.port 8501
    }
    "2" {
        Write-Host "Starting YouTube Channel Analyzer at http://localhost:8501" -ForegroundColor Yellow
        streamlit run youtube_analyzer_streamlit.py --server.port 8501
    }
    "3" {
        Write-Host "Starting YouTube Analyzer (Skills & Tools) at http://localhost:8501" -ForegroundColor Magenta
        streamlit run youtube_analyzer_app.py --server.port 8501
    }
    default {
        Write-Host "Invalid choice. Starting Main App..." -ForegroundColor Red
        streamlit run main_app.py --server.port 8501
    }
}
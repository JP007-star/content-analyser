@echo off
title Content Analyser - JP Cinematic Universe
echo.
echo ============================================
echo  🔱 Content Analyser - JP Cinematic Universe
echo ============================================
echo.
echo Select app to run:
echo   1. Main App (Both Analyzers)
echo   2. YouTube Channel Analyzer (API-based)
echo   3. YouTube Analyzer (Skills & Tools)
echo.
set /p choice="Enter choice (1-3) [default=1]: "
if "%choice%"=="" set choice=1

cd /d "%~dp0"

if "%choice%"=="1" (
    echo Starting Main App at http://localhost:8501
    streamlit run main_app.py --server.port 8501
) else if "%choice%"=="2" (
    echo Starting YouTube Channel Analyzer at http://localhost:8501
    streamlit run youtube_analyzer_streamlit.py --server.port 8501
) else if "%choice%"=="3" (
    echo Starting YouTube Analyzer (Skills & Tools) at http://localhost:8501
    streamlit run youtube_analyzer_app.py --server.port 8501
) else (
    echo Invalid choice. Starting Main App...
    streamlit run main_app.py --server.port 8501
)

pause
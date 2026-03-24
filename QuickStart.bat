@echo off
chcp 65001 >nul
title A股自选股智能分析系统

echo ============================================================
echo              A股自选股智能分析系统
echo                    Stock Analysis System
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not detected. Please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python installed
echo.

REM Check .env file
if not exist ".env" (
    echo [INFO] .env configuration file not found
    echo.
    echo Creating .env from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] .env file created
        echo.
        echo ============================================================
        echo     Please edit .env file and add your LLM API Key
        echo ============================================================
        echo.
        echo Recommended options:
        echo   1. Google Gemini (Free tier available)
        echo      Visit: https://aistudio.google.com/
        echo.
        echo   2. DeepSeek (Cost-effective)
        echo      Visit: https://platform.deepseek.com/
        echo.
        notepad .env
        echo.
        echo After configuration, press any key to continue...
        pause >nul
    ) else (
        echo [ERROR] .env.example file not found
        pause
        exit /b 1
    )
)

echo ============================================================
echo           Select Launch Mode
echo ============================================================
echo.
echo   1. Web Interface (Recommended)
echo      Start Web service, use in browser
echo.
echo   2. Command Line Mode
echo      Analyze stocks configured in .env
echo.
echo   3. Debug Mode
echo      View detailed logs for troubleshooting
echo.
echo   4. Market Review Only
echo      Only analyze market, skip individual stocks
echo.
echo   5. Exit
echo.

set /p choice="Please select (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting Web service...
    echo Access: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
    echo.
    echo Press Ctrl+C to stop service
    echo.
    python main.py --serve-only --port 8000
) else if "%choice%"=="2" (
    echo.
    echo Starting stock analysis...
    echo.
    python main.py
    echo.
    pause
) else if "%choice%"=="3" (
    echo.
    echo Running in debug mode...
    echo.
    python main.py --debug
    echo.
    pause
) else if "%choice%"=="4" (
    echo.
    echo Executing market review...
    echo.
    python main.py --market-review --no-notify
    echo.
    pause
) else if "%choice%"=="5" (
    exit /b 0
) else (
    echo.
    echo Invalid selection, exiting...
    pause
    exit /b 1
)

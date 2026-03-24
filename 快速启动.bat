@echo off
chcp 65001 >nul
title A股自选股智能分析系统

echo ============================================================
echo              A股自选股智能分析系统
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python已安装
echo.

REM 检查.env文件
if not exist ".env" (
    echo [提示] 未找到.env配置文件
    echo.
    echo 正在从.env.example创建.env文件...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] 已创建.env文件
        echo.
        echo ============================================================
        echo     请编辑.env文件，填入您的LLM API密钥
        echo ============================================================
        echo.
        echo 推荐配置：
        echo   1. Google Gemini（有免费额度）
        echo      访问: https://aistudio.google.com/
        echo.
        echo   2. DeepSeek（性价比高）
        echo      访问: https://platform.deepseek.com/
        echo.
        notepad .env
        echo.
        echo 配置完成后按任意键继续...
        pause >nul
    ) else (
        echo [错误] 未找到.env.example文件
        pause
        exit /b 1
    )
)

echo ============================================================
echo           选择启动模式
echo ============================================================
echo.
echo   1. Web界面模式（推荐）
echo      启动Web服务，在浏览器中使用
echo.
echo   2. 命令行模式
echo      分析.env中配置的股票
echo.
echo   3. 调试模式
echo      查看详细日志，用于问题排查
echo.
echo   4. 仅大盘复盘
echo      只执行大盘分析，不分析个股
echo.
echo   5. 退出
echo.

set /p choice="请选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 启动Web服务...
    echo 访问地址: http://localhost:8000
    echo API文档: http://localhost:8000/docs
    echo.
    echo 按 Ctrl+C 停止服务
    echo.
    python main.py --serve-only --port 8000
) else if "%choice%"=="2" (
    echo.
    echo 开始分析股票...
    echo.
    python main.py
    echo.
    pause
) else if "%choice%"=="3" (
    echo.
    echo 调试模式运行...
    echo.
    python main.py --debug
    echo.
    pause
) else if "%choice%"=="4" (
    echo.
    echo 执行大盘复盘...
    echo.
    python main.py --market-review --no-notify
    echo.
    pause
) else if "%choice%"=="5" (
    exit /b 0
) else (
    echo.
    echo 无效选择，退出...
    pause
    exit /b 1
)

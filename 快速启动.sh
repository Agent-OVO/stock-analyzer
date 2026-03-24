#!/bin/bash

# A股自选股智能分析系统 - 快速启动脚本

echo "============================================================"
echo "           A股自选股智能分析系统"
echo "============================================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装"
    echo "Mac: brew install python@3.10"
    echo "Ubuntu: sudo apt install python3.10"
    exit 1
fi

echo "[OK] Python已安装: $(python3 --version)"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "[提示] 未找到.env配置文件"
    echo ""
    echo "正在从.env.example创建.env文件..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[OK] 已创建.env文件"
        echo ""
        echo "============================================================"
        echo "     请编辑.env文件，填入您的LLM API密钥"
        echo "============================================================"
        echo ""
        echo "推荐配置："
        echo "  1. Google Gemini（有免费额度）"
        echo "     访问: https://aistudio.google.com/"
        echo ""
        echo "  2. DeepSeek（性价比高）"
        echo "     访问: https://platform.deepseek.com/"
        echo ""
        read -p "按Enter继续编辑.env文件..."
        ${EDITOR:-nano} .env
    else
        echo "[错误] 未找到.env.example文件"
        exit 1
    fi
fi

echo "============================================================"
echo "           选择启动模式"
echo "============================================================"
echo ""
echo "  1. Web界面模式（推荐）"
echo "     启动Web服务，在浏览器中使用"
echo ""
echo "  2. 命令行模式"
echo "     分析.env中配置的股票"
echo ""
echo "  3. 调试模式"
echo "     查看详细日志，用于问题排查"
echo ""
echo "  4. 仅大盘复盘"
echo "     只执行大盘分析，不分析个股"
echo ""
echo "  5. 退出"
echo ""
read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "启动Web服务..."
        echo "访问地址: http://localhost:8000"
        echo "API文档: http://localhost:8000/docs"
        echo ""
        echo "按 Ctrl+C 停止服务"
        echo ""
        python3 main.py --serve-only --port 8000
        ;;
    2)
        echo ""
        echo "开始分析股票..."
        echo ""
        python3 main.py
        ;;
    3)
        echo ""
        echo "调试模式运行..."
        echo ""
        python3 main.py --debug
        ;;
    4)
        echo ""
        echo "执行大盘复盘..."
        echo ""
        python3 main.py --market-review --no-notify
        ;;
    5)
        echo "退出..."
        exit 0
        ;;
    *)
        echo ""
        echo "无效选择，退出..."
        exit 1
        ;;
esac

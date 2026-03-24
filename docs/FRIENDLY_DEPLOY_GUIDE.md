# Quick Start Guide for Friends

Thank you for your interest in the A股自选股智能分析系统!

---

## Step 1: Get the Code

Clone the repository:
```bash
git clone <repository-url>
cd 股票智能分析系统
```

---

## Step 2: Install Python

**Windows**: https://www.python.org/downloads/ (Install Python 3.10+)
**Mac**: `brew install python@3.10`
**Linux**: `sudo apt install python3.10`

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If it fails, try:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Step 4: Configure LLM API

Choose one of the following providers:

### Option 1: Google Gemini (Recommended for beginners)

1. Get API Key: https://aistudio.google.com/
2. Configure:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

### Option 2: DeepSeek (Cost-effective)

1. Get API Key: https://platform.deepseek.com/
2. Configure:
   ```bash
   DEEPSEEK_API_KEY=your_api_key_here
   DEEPSEEK_BASE_URL=https://api.deepseek.com
   ```

### Option 3: OpenAI

1. Get API Key: https://platform.openai.com/
2. Configure:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

### Option 4: Ollama (Local, Free)

1. Install: https://ollama.com/
2. Pull model: `ollama pull qwen2.5:7b`
3. Configure:
   ```bash
   OPENAI_API_BASE=http://localhost:11434/v1
   OPENAI_API_KEY=ollama
   LLM_MODEL=openai/qwen2.5:7b
   ```

---

## Step 5: Configure Stock List

Edit `.env`:
```bash
STOCK_LIST=600519,000001,300750
```

Common stock codes:
- 600519: 贵州茅台
- 000001: 平安银行
- 300750: 宁德时代
- 600036: 招商银行
- 000002: 万科A

---

## Step 6: Start the System

### Windows
Double-click `快速启动.bat`

### Mac/Linux
```bash
chmod +x 快速启动.sh
./快速启动.sh
```

### Or use command line:
```bash
# Web interface
python main.py --serve-only --port 8000
# Visit: http://localhost:8000

# Analyze stocks
python main.py

# Debug mode
python main.py --debug
```

---

## Complete .env Example

```bash
# LLM Configuration (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Stock Configuration
STOCK_LIST=600519,000001,300750

# Optional: Notifications
# WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
# DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
# FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# System Configuration
DEBUG=false
LOG_LEVEL=INFO
REPORT_LANGUAGE=zh-CN
```

---

## Troubleshooting

**Q: "未检测到 API Key"**
A: Check `.env` file exists and API Key is correct.

**Q: API call failed**
A:
1. Verify API Key has sufficient quota
2. If using Gemini, check network can access Google services
3. If proxy needed:
   ```bash
   HTTP_PROXY=http://127.0.0.1:10809
   HTTPS_PROXY=http://127.0.0.1:10809
   ```

**Q: Dependencies installation failed**
A:
1. Upgrade pip: `python -m pip install --upgrade pip`
2. Use mirror source
3. Install individually: `pip install package_name`

**Q: How to stop Web service**
A: Press `Ctrl+C` in the terminal

---

## Need Help?

- Full documentation: `docs/DEPLOY.md`
- GitHub Issues: Report problems here
- API Docs: http://localhost:8000/docs (after starting Web service)

**Enjoy using the system! 🎉**

# Quick Start Guide

## ⚡ 3-Step Setup

### 1️⃣ Install Ollama + Llama 3.2

```bash
# Install Ollama from https://ollama.ai
# Then:
ollama pull llama3.2
ollama serve  # Keep this running
```

### 2️⃣ Install Dependencies

```bash
cd comm-scanner
pip install -r requirements.txt
```

### 3️⃣ Configure & Run

```bash
# Edit config/config.json with your email credentials
nano config/config.json
# or
vim config/config.json

# Test setup
python3 test_setup.py

# Run scanner
python3 src/scanner.py
```

## 📧 Gmail Quick Config

```json
{
  "email": {
    "enabled": true,
    "address": "you@gmail.com",
    "password": "xxxx xxxx xxxx xxxx",  
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "scan_days": 7,
    "max_messages": 50
  }
}
```

**Get Gmail App Password:**
1. https://myaccount.google.com
2. Security → 2-Step Verification (enable)
3. Security → App passwords → Generate
4. Use the 16-character password above

## 🔍 Verify Everything Works

```bash
python3 test_setup.py
```

Should see:
```
✓ PASS - Python Version
✓ PASS - Dependencies
✓ PASS - Ollama Connection
✓ PASS - Llama 3.2 Model
✓ PASS - LLM Query
```

## 🚀 Run First Scan

```bash
python3 src/scanner.py
```

Results saved to `data/results/`

## ⚠️ Common Issues

**"Cannot connect to Ollama"**
```bash
ollama serve  # Start Ollama
```

**"Model not found"**
```bash
ollama pull llama3.2
```

**"Email failed" (Gmail)**
- Use App Password (not regular password)
- Enable IMAP in Gmail settings

## 📖 Full Documentation

See `README.md` for complete documentation.

---

**Time to First Scan:** ~5 minutes

**Status:** ✅ All code verified

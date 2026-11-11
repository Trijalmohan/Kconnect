# Communication Scanner - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Install Ollama + Llama 3.2
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama serve
```

### 2. Install Dependencies
```bash
cd comm-scanner
pip install -r requirements.txt
```

### 3. Configure & Run
```bash
# Edit config/config.json with your email credentials
# Then run:
python src/scanner.py
```

---

## 📧 Email Configuration Examples

### Gmail
```json
{
  "email": {
    "enabled": true,
    "address": "you@gmail.com",
    "password": "your-app-password",  // Get from Google Account → Security → App Passwords
    "imap_server": "imap.gmail.com",
    "imap_port": 993
  }
}
```

### Outlook/Office 365
```json
{
  "email": {
    "enabled": true,
    "address": "you@outlook.com",
    "password": "your-password",
    "imap_server": "outlook.office365.com",
    "imap_port": 993
  }
}
```

---

## 🎯 What It Does

Scans your emails and uses **local Llama 3.2** to:
- ✅ Filter useful messages from noise
- 📅 Extract meeting dates & times
- ✔️ Identify action items & tasks  
- ⏰ Find deadlines
- 👥 Detect mentioned people
- 🚨 Assess urgency (Low/Medium/High)

---

## 📁 Output Files

Results saved to `data/results/`:
- `scan_results_TIMESTAMP.json` - All analyzed messages
- `useful_messages_only.json` - Only useful messages

---

## 🔧 Common Issues

**"Cannot connect to Ollama"**
```bash
ollama serve  # Start Ollama server
```

**"Model not found"**
```bash
ollama pull llama3.2
```

**"Email connection failed" (Gmail)**
- Use App Password, not regular password
- Enable 2FA first, then create App Password
- Go to: Google Account → Security → App Passwords

**"Email connection failed" (Other)**
- Check IMAP is enabled in email settings
- Verify server address is correct
- Some providers need "less secure apps" enabled

---

## 🛠️ Customization

### Scan more/fewer days
Edit `config/config.json`:
```json
"scan_days": 14  // Scan last 14 days
```

### Scan more/fewer messages
```json
"max_messages": 100  // Scan up to 100 messages
```

---

## 🔒 Privacy

- ✅ 100% local processing (Llama 3.2 via Ollama)
- ✅ No cloud API calls
- ✅ Your data never leaves your machine
- ✅ All results stored locally

---

## 💡 Tips

1. **First scan is slow** - Ollama loads model into memory
2. **Subsequent scans are faster** - Model stays loaded
3. **Use GPU if available** - Ollama auto-detects
4. **Start small** - Test with 7 days, 50 messages first
5. **Check sample output** - See `data/results/sample_output.json`

---

## 📊 Example Output

```
SCAN SUMMARY
================================================================================
Total messages scanned: 23
Useful messages found: 8
Filtered out: 15

Urgency breakdown:
  High:   2
  Medium: 3
  Low:    3

TOP USEFUL MESSAGES
================================================================================
[HIGH] Production Issue - Needs Immediate Attention
From: oncall@company.com
Summary: Critical production issue requiring immediate response
Action items: Check deployments, Review logs, Roll back if needed
Deadlines: 15 minutes to acknowledge

[MEDIUM] Team Standup Tomorrow - 10 AM
From: manager@company.com
Summary: Weekly team standup meeting scheduled
Dates: Tuesday 10 AM
Action items: Prepare sprint updates, Identify blockers
```

---

## 🚧 Future Channels (Extensible Design)

The app is designed to support:
- Slack
- Microsoft Teams  
- Discord
- Any IMAP email

See README.md for extension examples.

---

**Need help?** Check the full README.md or run `python test_setup.py` to verify your setup.

# Windows Quick Start Guide

## Prerequisites
1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Install Ollama from [ollama.ai](https://ollama.ai)

## Setup Steps

### 1. Install Ollama and Llama 3.2

Open PowerShell or Command Prompt:

```powershell
# Pull llama3.2 model
ollama pull llama3.2

# Start Ollama (if not auto-started)
ollama serve
```

### 2. Install Python Dependencies

Open PowerShell in the comm-scanner directory:

```powershell
pip install -r requirements.txt
```

### 3. Configure Email

1. Copy `config\config.example.json` to `config\config.json`
2. Edit `config\config.json` with your email settings

For Gmail:
- Use an App Password (see README.md for instructions)
- Set `imap_server` to `imap.gmail.com`

For Outlook:
- Set `imap_server` to `outlook.office365.com`

### 4. Test Setup

```powershell
python test_setup.py
```

### 5. Run Scanner

```powershell
python src\scanner.py
```

## Troubleshooting

### "Ollama is not running"
- Open Task Manager and check if Ollama is running
- Start Ollama from the Start Menu
- Or run `ollama serve` in PowerShell

### "Cannot connect to email"
- For Gmail: Make sure you're using an App Password
- Check Windows Defender Firewall isn't blocking the connection
- Verify IMAP is enabled in your email settings

### "Python not found"
- Make sure Python is added to PATH during installation
- Restart PowerShell after installing Python

## Running in Background

To run the scanner automatically:

1. Create a Task in Task Scheduler
2. Set trigger (daily, weekly, etc.)
3. Set action: `python.exe` with arguments `src\scanner.py`
4. Set "Start in" directory to your comm-scanner folder

---

For more details, see README.md

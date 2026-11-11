# Usage Examples

## Example 1: Basic Email Scan (Gmail)

### Configuration
```json
{
  "email": {
    "enabled": true,
    "address": "john.doe@gmail.com",
    "password": "abcd efgh ijkl mnop",
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "scan_days": 7,
    "max_messages": 20
  }
}
```

### Command
```bash
python3 src/scanner.py
```

### Expected Output
```
╔══════════════════════════════════════════════════════════════╗
║         COMMUNICATION SCANNER - Local LLM Analysis           ║
║                  Powered by Llama 3.2                        ║
╚══════════════════════════════════════════════════════════════╝

================================================================================
SYSTEM CHECK
================================================================================

Checking Ollama connection... ✓
Checking for llama3.2 model... ✓

System check passed!

================================================================================
SETUP SCANNERS
================================================================================

Connecting to imap.gmail.com... ✓

================================================================================
SCANNING MESSAGES
================================================================================

Searching messages since 03-Feb-2026... ✓
Found 42 messages (processing 20 most recent)

[1/20] Fetching message... ✓
[2/20] Fetching message... ✓
...
[20/20] Fetching message... ✓

================================================================================
Analyzing 20 messages with Llama 3.2
================================================================================

[1/20] Team Standup Tomorrow - 10 AM
  Calling Ollama... ✓
  Useful: True | Urgency: medium

[2/20] Newsletter: Weekly Tech News
  Calling Ollama... ✓
  Useful: False | Urgency: low

...

================================================================================
SAVING RESULTS
================================================================================

✓ All messages saved to: data/results/scan_results_20260210_100532.json
✓ Useful messages saved to: data/results/useful_messages_only.json

================================================================================
SCAN SUMMARY
================================================================================

Total messages scanned: 20
Useful messages found: 7
Filtered out: 13

Urgency breakdown:
  High:   1
  Medium: 3
  Low:    3

================================================================================
TOP USEFUL MESSAGES
================================================================================

[HIGH] URGENT: Server Maintenance Tonight
From: ops@company.com
Summary: Critical server maintenance scheduled requiring action
Action items: Backup data, Notify team, Monitor systems
Deadlines: Tonight 11 PM

[MEDIUM] Team Standup Tomorrow - 10 AM
From: manager@company.com
Summary: Weekly team sync meeting scheduled
Dates: Tomorrow 10 AM
Action items: Prepare sprint update, Review blockers

[MEDIUM] Code Review Request - PR #234
From: colleague@company.com
Summary: Pull request needs review before merge
Action items: Review code changes, Test locally, Provide feedback
Deadlines: End of week

...

================================================================================
SCAN COMPLETE!
================================================================================
```

---

## Example 2: Outlook Email Scan

### Configuration
```json
{
  "email": {
    "enabled": true,
    "address": "jane.smith@outlook.com",
    "password": "your-password",
    "imap_server": "outlook.office365.com",
    "imap_port": 993,
    "scan_days": 3,
    "max_messages": 30
  }
}
```

### Results
- Scans last 3 days
- Analyzes up to 30 messages
- Same output format as Example 1

---

## Example 3: JSON Output Structure

### All Messages (`scan_results_TIMESTAMP.json`)

```json
[
  {
    "id": "12345",
    "subject": "Team Standup Tomorrow - 10 AM",
    "from": "Sarah Johnson <manager@company.com>",
    "date": "Mon, 09 Feb 2026 14:30:00 -0800",
    "body": "Hi team,\n\nJust a reminder we have standup tomorrow at 10 AM...",
    "source": "email",
    "analysis": {
      "is_useful": true,
      "summary": "Reminder about weekly team standup meeting scheduled for tomorrow morning",
      "key_points": {
        "dates": [
          "Tomorrow 10 AM",
          "Tuesday February 10"
        ],
        "meetings": [
          "Weekly team standup in conference room B"
        ],
        "action_items": [
          "Prepare sprint progress update",
          "Identify any blockers",
          "Review upcoming week priorities"
        ],
        "deadlines": [],
        "people": [
          "Sarah Johnson",
          "Engineering team"
        ]
      },
      "urgency": "medium",
      "category": "meeting"
    }
  },
  {
    "id": "12346",
    "subject": "URGENT: Production Issue - Immediate Action Required",
    "from": "Ops Team <ops@company.com>",
    "date": "Mon, 09 Feb 2026 16:45:00 -0800",
    "body": "ALERT: We're experiencing 15% error rate on API endpoints...",
    "source": "email",
    "analysis": {
      "is_useful": true,
      "summary": "Critical production issue with elevated API error rates requiring immediate investigation",
      "key_points": {
        "dates": [
          "Now"
        ],
        "meetings": [],
        "action_items": [
          "Check recent deployments",
          "Review application logs",
          "Roll back if necessary",
          "Acknowledge within 15 minutes"
        ],
        "deadlines": [
          "15 minutes - acknowledgment required",
          "1 hour - resolution or escalation"
        ],
        "people": [
          "On-call engineer",
          "DevOps team"
        ]
      },
      "urgency": "high",
      "category": "task"
    }
  },
  {
    "id": "12347",
    "subject": "Newsletter: This Week in Tech",
    "from": "TechNews Weekly <newsletter@technews.com>",
    "date": "Mon, 09 Feb 2026 08:00:00 -0800",
    "body": "Top stories this week:\n1. New AI model released\n2. Tech IPO announced...",
    "source": "email",
    "analysis": {
      "is_useful": false,
      "summary": "Weekly tech newsletter with industry news and updates",
      "key_points": {
        "dates": [],
        "meetings": [],
        "action_items": [],
        "deadlines": [],
        "people": []
      },
      "urgency": "low",
      "category": "information"
    }
  }
]
```

### Useful Messages Only (`useful_messages_only.json`)

Same structure, but only messages where `"is_useful": true`

---

## Example 4: Using Results Programmatically

### Python Script to Read Results

```python
import json
from pathlib import Path

# Load results
results_file = Path("data/results/useful_messages_only.json")
with open(results_file) as f:
    messages = json.load(f)

# Find high urgency items
high_urgency = [
    msg for msg in messages 
    if msg['analysis']['urgency'] == 'high'
]

print(f"Found {len(high_urgency)} high urgency messages:")
for msg in high_urgency:
    print(f"\n- {msg['subject']}")
    print(f"  From: {msg['from']}")
    
    action_items = msg['analysis']['key_points'].get('action_items', [])
    if action_items:
        print(f"  Actions: {', '.join(action_items[:3])}")
    
    deadlines = msg['analysis']['key_points'].get('deadlines', [])
    if deadlines:
        print(f"  Deadlines: {', '.join(deadlines)}")
```

### Output
```
Found 2 high urgency messages:

- URGENT: Production Issue - Immediate Action Required
  From: Ops Team <ops@company.com>
  Actions: Check deployments, Review logs, Roll back if necessary
  Deadlines: 15 minutes - acknowledgment, 1 hour - resolution

- Critical: Budget Approval Needed by EOD
  From: Finance <finance@company.com>
  Actions: Review budget, Get approvals, Submit form
  Deadlines: End of day today
```

---

## Example 5: Filter Messages by Category

### Script
```python
import json
from collections import defaultdict

with open("data/results/useful_messages_only.json") as f:
    messages = json.load(f)

# Group by category
by_category = defaultdict(list)
for msg in messages:
    category = msg['analysis']['category']
    by_category[category].append(msg['subject'])

# Display
for category, subjects in by_category.items():
    print(f"\n{category.upper()} ({len(subjects)}):")
    for subject in subjects[:5]:  # Show first 5
        print(f"  - {subject}")
```

### Output
```
MEETING (4):
  - Team Standup Tomorrow - 10 AM
  - Q1 Planning Session - Feb 15
  - 1:1 with Manager - Thursday
  - All Hands Meeting - Next Week

TASK (5):
  - Code Review Request - PR #234
  - Update Documentation by Friday
  - Security Patch Required
  - Database Migration Needed
  - User Story Clarification

INFORMATION (2):
  - New Policy Update
  - Office Closure - Holiday
```

---

## Example 6: Extract All Deadlines

### Script
```python
import json
from datetime import datetime

with open("data/results/useful_messages_only.json") as f:
    messages = json.load(f)

# Collect all deadlines
all_deadlines = []
for msg in messages:
    deadlines = msg['analysis']['key_points'].get('deadlines', [])
    for deadline in deadlines:
        all_deadlines.append({
            'deadline': deadline,
            'subject': msg['subject'],
            'from': msg['from']
        })

# Sort by urgency
print("ALL UPCOMING DEADLINES:")
print("=" * 60)
for item in all_deadlines:
    print(f"\n{item['deadline']}")
    print(f"  Task: {item['subject']}")
    print(f"  From: {item['from']}")
```

---

## Example 7: Custom Search in Results

### Find Messages About Specific Topic
```python
import json

def search_messages(keyword, field='subject'):
    """Search for keyword in messages"""
    with open("data/results/scan_results_20260210_100532.json") as f:
        messages = json.load(f)
    
    results = []
    for msg in messages:
        # Search in specified field
        text = msg.get(field, '').lower()
        if keyword.lower() in text:
            results.append(msg)
    
    return results

# Search for "deployment" in subject
deployment_msgs = search_messages("deployment", "subject")
print(f"Found {len(deployment_msgs)} messages about deployments")

# Search for "urgent" in body
urgent_msgs = search_messages("urgent", "body")
print(f"Found {len(urgent_msgs)} urgent messages")
```

---

## Example 8: Testing Different Configurations

### Small Scan (Recent Messages Only)
```json
{
  "email": {
    "enabled": true,
    "address": "you@gmail.com",
    "password": "your-app-password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "scan_days": 1,
    "max_messages": 10
  }
}
```
**Use case:** Quick daily check

### Large Scan (Weekly Deep Dive)
```json
{
  "email": {
    "enabled": true,
    "address": "you@gmail.com",
    "password": "your-app-password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "scan_days": 14,
    "max_messages": 100
  }
}
```
**Use case:** Weekly comprehensive review

---

## Example 9: Troubleshooting Workflow

### 1. Test Ollama First
```bash
curl http://localhost:11434/api/tags
```

### 2. Test Llama 3.2 Directly
```bash
ollama run llama3.2 "Hello, are you working?"
```

### 3. Run Setup Test
```bash
python3 test_setup.py
```

### 4. Test Email Connection (without LLM)
```python
from src.scanner import EmailScanner

scanner = EmailScanner(
    "you@gmail.com",
    "your-app-password",
    "imap.gmail.com"
)

if scanner.connect():
    print("✓ Email connection works")
    messages = scanner.scan_recent_messages(days=1, max_messages=5)
    print(f"✓ Found {len(messages)} messages")
    scanner.disconnect()
else:
    print("✗ Email connection failed")
```

---

## Example 10: Scheduled Scanning (Linux/Mac)

### Create Cron Job
```bash
# Run every day at 8 AM
0 8 * * * cd /path/to/comm-scanner && python3 src/scanner.py >> logs/cron.log 2>&1

# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/comm-scanner && python3 src/scanner.py >> logs/cron.log 2>&1
```

### Create Systemd Timer (Linux)
```ini
# /etc/systemd/user/comm-scanner.service
[Unit]
Description=Communication Scanner

[Service]
Type=oneshot
WorkingDirectory=/path/to/comm-scanner
ExecStart=/usr/bin/python3 src/scanner.py

# /etc/systemd/user/comm-scanner.timer
[Unit]
Description=Run Communication Scanner Daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
systemctl --user enable comm-scanner.timer
systemctl --user start comm-scanner.timer
```

---

**For more examples, see README.md**

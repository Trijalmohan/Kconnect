#!/usr/bin/env python3
"""
Communication Scanner - Scans emails and extracts key information using local Llama 3.2
"""

import imaplib
import email
from email.header import decode_header
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import time
import sys

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback for no color support
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = ''
    class Style:
        BRIGHT = RESET_ALL = ''


class OllamaLLM:
    """Interface for local Llama 3.2 via Ollama"""
    
    def __init__(self, model="llama3.2", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def analyze_message(self, text: str) -> Dict[str, Any]:
        """Analyze message text and extract key information"""
        
        # Truncate very long messages
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        prompt = f"""Analyze this message and extract key information. Return ONLY valid JSON.

Message:
{text}

Return JSON in this EXACT format (no extra text):
{{
    "is_useful": true,
    "summary": "brief summary",
    "key_points": {{
        "dates": ["list of dates"],
        "meetings": ["list of meetings"],
        "action_items": ["list of tasks"],
        "deadlines": ["list of deadlines"],
        "people": ["list of people"]
    }},
    "urgency": "high",
    "category": "meeting"
}}

Urgency must be: low, medium, or high
Category must be: meeting, task, information, or other
is_useful: true if message contains actionable items, meetings, deadlines, or important info"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            print(f"{Fore.CYAN}  Calling Ollama...", end="", flush=True)
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            # Parse the LLM's JSON response
            llm_response = result.get('response', '{}')
            analysis = json.loads(llm_response)
            
            # Validate required fields
            required_fields = ['is_useful', 'summary', 'key_points', 'urgency', 'category']
            for field in required_fields:
                if field not in analysis:
                    print(f"{Fore.YELLOW} Missing field: {field}")
                    analysis[field] = self._get_default_value(field)
            
            print(f"{Fore.GREEN} ✓")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED} JSON Error: {e}")
            return self._get_default_analysis("JSON parsing error")
        except requests.exceptions.Timeout:
            print(f"{Fore.RED} Timeout")
            return self._get_default_analysis("Request timeout")
        except Exception as e:
            print(f"{Fore.RED} Error: {str(e)[:50]}")
            return self._get_default_analysis(f"Error: {e}")
    
    def _get_default_value(self, field: str):
        """Get default value for missing field"""
        defaults = {
            'is_useful': False,
            'summary': 'Could not analyze',
            'key_points': {
                'dates': [],
                'meetings': [],
                'action_items': [],
                'deadlines': [],
                'people': []
            },
            'urgency': 'low',
            'category': 'other'
        }
        return defaults.get(field, None)
    
    def _get_default_analysis(self, error_msg: str) -> Dict[str, Any]:
        """Return default analysis on error"""
        return {
            "is_useful": False,
            "summary": error_msg,
            "key_points": {
                "dates": [],
                "meetings": [],
                "action_items": [],
                "deadlines": [],
                "people": []
            },
            "urgency": "low",
            "category": "other"
        }
    
    def check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            print(f"{Fore.CYAN}Checking Ollama connection...", end="", flush=True)
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            print(f"{Fore.GREEN} ✓")
            
            models = response.json().get('models', [])
            
            print(f"{Fore.CYAN}Checking for {self.model} model...", end="", flush=True)
            model_available = any(self.model in model.get('name', '') for model in models)
            
            if not model_available:
                print(f"{Fore.RED} ✗")
                print(f"\n{Fore.YELLOW}Model '{self.model}' not found.")
                print(f"{Fore.CYAN}Available models:")
                for model in models:
                    print(f"  - {model.get('name')}")
                print(f"\n{Fore.CYAN}To install: {Fore.WHITE}ollama pull {self.model}")
                return False
            
            print(f"{Fore.GREEN} ✓")
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED} ✗")
            print(f"\n{Fore.RED}Cannot connect to Ollama at {self.base_url}")
            print(f"{Fore.CYAN}Make sure Ollama is running:")
            print(f"{Fore.WHITE}  ollama serve")
            return False
        except Exception as e:
            print(f"{Fore.RED} ✗")
            print(f"{Fore.RED}Error: {e}")
            return False


class EmailScanner:
    """Scans email via IMAP"""
    
    def __init__(self, email_address: str, password: str, imap_server: str, imap_port: int = 993):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.mail = None
    
    def connect(self) -> bool:
        """Connect to email server"""
        try:
            print(f"{Fore.CYAN}Connecting to {self.imap_server}...", end="", flush=True)
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_address, self.password)
            print(f"{Fore.GREEN} ✓")
            return True
        except imaplib.IMAP4.error as e:
            print(f"{Fore.RED} ✗")
            print(f"{Fore.RED}IMAP Error: {e}")
            print(f"{Fore.YELLOW}Check your email/password and IMAP settings")
            return False
        except Exception as e:
            print(f"{Fore.RED} ✗")
            print(f"{Fore.RED}Connection Error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from email server"""
        if self.mail:
            try:
                self.mail.logout()
            except:
                pass
    
    def scan_recent_messages(self, days: int = 7, max_messages: int = 50) -> List[Dict[str, Any]]:
        """Scan recent email messages"""
        messages = []
        
        try:
            self.mail.select('INBOX')
            
            # Search for messages from the last N days
            date_since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            
            print(f"{Fore.CYAN}Searching messages since {date_since}...", end="", flush=True)
            _, message_numbers = self.mail.search(None, f'SINCE {date_since}')
            print(f"{Fore.GREEN} ✓")
            
            message_ids = message_numbers[0].split()
            total_found = len(message_ids)
            
            # Limit to most recent messages
            message_ids = message_ids[-max_messages:]
            
            print(f"{Fore.GREEN}Found {total_found} messages (processing {len(message_ids)} most recent)")
            
            for i, msg_id in enumerate(message_ids, 1):
                try:
                    print(f"{Fore.CYAN}[{i}/{len(message_ids)}] Fetching message...", end="", flush=True)
                    _, msg_data = self.mail.fetch(msg_id, '(RFC822)')
                    
                    if msg_data[0] is None:
                        print(f"{Fore.YELLOW} Skipped (empty)")
                        continue
                    
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Decode subject
                    subject = self._decode_header(email_message['Subject'])
                    sender = email_message['From']
                    date = email_message['Date']
                    
                    # Get email body
                    body = self._get_email_body(email_message)
                    
                    print(f"{Fore.GREEN} ✓")
                    
                    messages.append({
                        'id': msg_id.decode(),
                        'subject': subject or "(No Subject)",
                        'from': sender or "(Unknown)",
                        'date': date or "",
                        'body': body,
                        'source': 'email'
                    })
                    
                except Exception as e:
                    print(f"{Fore.YELLOW} Error: {str(e)[:30]}")
                    continue
            
        except Exception as e:
            print(f"{Fore.RED}Error scanning emails: {e}")
        
        return messages
    
    def _decode_header(self, header):
        """Decode email header"""
        if header is None:
            return ""
        
        try:
            decoded_header = decode_header(header)
            header_parts = []
            
            for content, encoding in decoded_header:
                if isinstance(content, bytes):
                    try:
                        header_parts.append(content.decode(encoding or 'utf-8'))
                    except:
                        header_parts.append(content.decode('utf-8', errors='ignore'))
                else:
                    header_parts.append(str(content))
            
            return ''.join(header_parts)
        except:
            return str(header)
    
    def _get_email_body(self, email_message):
        """Extract email body text"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                                break
                        except:
                            pass
            else:
                try:
                    payload = email_message.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                    else:
                        body = str(email_message.get_payload())
                except:
                    body = str(email_message.get_payload())
        except:
            body = ""
        
        # Limit body length
        return body[:5000] if body else ""


class CommunicationScanner:
    """Main scanner that coordinates all communication channels"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.llm = OllamaLLM(model="llama3.2")
        self.scanners = []
        self.results_dir = Path("data/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load configuration file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            print(f"{Fore.YELLOW}Config file not found: {self.config_path}")
            print(f"{Fore.CYAN}Creating default config file...")
            self._create_default_config()
            return self._load_config()
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Invalid JSON in config file: {e}")
            return {}
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "email": {
                "enabled": False,
                "address": "",
                "password": "",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "scan_days": 7,
                "max_messages": 50
            }
        }
        
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"{Fore.GREEN}Created config file: {self.config_path}")
        print(f"{Fore.YELLOW}Please edit it with your email credentials")
    
    def setup_email_scanner(self):
        """Setup email scanner if configured"""
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled', False):
            print(f"{Fore.YELLOW}Email scanning is disabled in config")
            print(f"{Fore.CYAN}Edit {self.config_path} and set 'enabled': true")
            return False
        
        email_address = email_config.get('address')
        password = email_config.get('password')
        imap_server = email_config.get('imap_server')
        
        if not email_address or not password:
            print(f"{Fore.YELLOW}Email credentials not configured")
            print(f"{Fore.CYAN}Edit {self.config_path} and add your email/password")
            return False
        
        scanner = EmailScanner(
            email_address, 
            password, 
            imap_server,
            email_config.get('imap_port', 993)
        )
        
        if scanner.connect():
            self.scanners.append(scanner)
            return True
        
        return False
    
    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan all configured communication channels"""
        all_messages = []
        
        for scanner in self.scanners:
            if isinstance(scanner, EmailScanner):
                days = self.config.get('email', {}).get('scan_days', 7)
                max_msgs = self.config.get('email', {}).get('max_messages', 50)
                messages = scanner.scan_recent_messages(days=days, max_messages=max_msgs)
                all_messages.extend(messages)
        
        return all_messages
    
    def analyze_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze all messages using LLM"""
        analyzed_messages = []
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}Analyzing {len(messages)} messages with Llama 3.2")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        for i, msg in enumerate(messages, 1):
            subject = msg.get('subject', 'No subject')
            print(f"\n{Fore.MAGENTA}[{i}/{len(messages)}] {subject[:60]}")
            
            # Combine subject and body for analysis
            text_to_analyze = f"Subject: {msg.get('subject', '')}\n\n{msg.get('body', '')}"
            
            analysis = self.llm.analyze_message(text_to_analyze)
            
            # Combine original message with analysis
            analyzed_msg = {
                **msg,
                'analysis': analysis
            }
            
            analyzed_messages.append(analyzed_msg)
            
            # Brief preview of analysis
            is_useful = analysis.get('is_useful', False)
            urgency = analysis.get('urgency', 'low')
            
            status_color = Fore.GREEN if is_useful else Fore.YELLOW
            print(f"  {status_color}Useful: {is_useful} | Urgency: {urgency}")
            
            # Small delay to avoid overwhelming the system
            time.sleep(0.3)
        
        return analyzed_messages
    
    def filter_useful_messages(self, analyzed_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter to only useful messages"""
        return [msg for msg in analyzed_messages if msg['analysis'].get('is_useful', False)]
    
    def save_results(self, messages: List[Dict[str, Any]], filename: str = None) -> Path:
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_results_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(messages, f, indent=2, default=str)
        
        return filepath
    
    def display_summary(self, messages: List[Dict[str, Any]]):
        """Display a summary of scanned messages"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{Style.BRIGHT}SCAN SUMMARY")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        useful_messages = [msg for msg in messages if msg['analysis'].get('is_useful', False)]
        
        print(f"{Fore.GREEN}Total messages scanned: {len(messages)}")
        print(f"{Fore.GREEN}Useful messages found: {len(useful_messages)}")
        print(f"{Fore.YELLOW}Filtered out: {len(messages) - len(useful_messages)}\n")
        
        # Group by urgency
        urgency_counts = {'high': 0, 'medium': 0, 'low': 0}
        for msg in useful_messages:
            urgency = msg['analysis'].get('urgency', 'low')
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
        
        print(f"{Fore.MAGENTA}Urgency breakdown:")
        print(f"  {Fore.RED}High:   {urgency_counts.get('high', 0)}")
        print(f"  {Fore.YELLOW}Medium: {urgency_counts.get('medium', 0)}")
        print(f"  {Fore.GREEN}Low:    {urgency_counts.get('low', 0)}\n")
        
        # Show top useful messages
        if useful_messages:
            print(f"{Fore.CYAN}{'='*80}")
            print(f"{Fore.CYAN}{Style.BRIGHT}TOP USEFUL MESSAGES")
            print(f"{Fore.CYAN}{'='*80}\n")
            
            # Sort by urgency
            urgency_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_messages = sorted(
                useful_messages, 
                key=lambda x: urgency_order.get(x['analysis'].get('urgency', 'low'), 3)
            )
            
            for i, msg in enumerate(sorted_messages[:10], 1):
                analysis = msg['analysis']
                urgency = analysis.get('urgency', 'low')
                
                urgency_color = {
                    'high': Fore.RED,
                    'medium': Fore.YELLOW,
                    'low': Fore.GREEN
                }.get(urgency, Fore.WHITE)
                
                print(f"{urgency_color}[{urgency.upper()}] {msg.get('subject', 'No subject')}")
                print(f"{Fore.WHITE}From: {msg.get('from', 'Unknown')}")
                print(f"{Fore.WHITE}Summary: {analysis.get('summary', 'No summary')}")
                
                key_points = analysis.get('key_points', {})
                if key_points.get('action_items'):
                    items = ', '.join(key_points['action_items'][:3])
                    print(f"{Fore.CYAN}Action items: {items}")
                if key_points.get('dates'):
                    dates = ', '.join(key_points['dates'][:3])
                    print(f"{Fore.MAGENTA}Dates: {dates}")
                if key_points.get('deadlines'):
                    deadlines = ', '.join(key_points['deadlines'][:2])
                    print(f"{Fore.RED}Deadlines: {deadlines}")
                
                print()
    
    def cleanup(self):
        """Cleanup resources"""
        for scanner in self.scanners:
            if isinstance(scanner, EmailScanner):
                scanner.disconnect()


def main():
    """Main application entry point"""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         COMMUNICATION SCANNER - Local LLM Analysis           ║")
    print("║                  Powered by Llama 3.2                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    # Initialize scanner
    scanner = CommunicationScanner()
    
    # Check if Ollama is available
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}SYSTEM CHECK")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    if not scanner.llm.check_availability():
        print(f"\n{Fore.RED}{'='*80}")
        print(f"{Fore.RED}Ollama not ready. Please fix the issues above.")
        print(f"{Fore.RED}{'='*80}\n")
        return 1
    
    print(f"\n{Fore.GREEN}System check passed!\n")
    
    # Setup scanners
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}SETUP SCANNERS")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    if not scanner.setup_email_scanner():
        print(f"\n{Fore.RED}{'='*80}")
        print(f"{Fore.RED}No scanners configured. Please configure email in config/config.json")
        print(f"{Fore.RED}{'='*80}\n")
        return 1
    
    # Scan messages
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}SCANNING MESSAGES")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    messages = scanner.scan_all()
    
    if not messages:
        print(f"\n{Fore.YELLOW}No messages found to analyze")
        scanner.cleanup()
        return 0
    
    # Analyze with LLM
    analyzed_messages = scanner.analyze_messages(messages)
    
    # Filter useful messages
    useful_messages = scanner.filter_useful_messages(analyzed_messages)
    
    # Save results
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}SAVING RESULTS")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    all_results_path = scanner.save_results(analyzed_messages)
    print(f"{Fore.GREEN}✓ All messages saved to: {all_results_path}")
    
    useful_results_path = scanner.save_results(useful_messages, "useful_messages_only.json")
    print(f"{Fore.GREEN}✓ Useful messages saved to: {useful_results_path}")
    
    # Display summary
    scanner.display_summary(analyzed_messages)
    
    # Cleanup
    scanner.cleanup()
    
    print(f"{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}{Style.BRIGHT}SCAN COMPLETE!")
    print(f"{Fore.GREEN}{'='*80}\n")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script to verify Communication Scanner setup
"""

import requests
import sys

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = ''
    class Style:
        BRIGHT = RESET_ALL = ''


def test_python_version():
    """Check Python version"""
    print(f"{Fore.CYAN}Checking Python version...", end="", flush=True)
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"{Fore.GREEN} ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"{Fore.RED} ✗ Python {version.major}.{version.minor}.{version.micro}")
        print(f"{Fore.YELLOW}  Python 3.8+ required")
        return False


def test_ollama_connection():
    """Test if Ollama is running"""
    print(f"{Fore.CYAN}Testing Ollama connection...", end="", flush=True)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print(f"{Fore.GREEN} ✓ Connected")
        return True
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED} ✗ Cannot connect")
        print(f"{Fore.YELLOW}  Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"{Fore.RED} ✗ Error: {e}")
        return False


def test_llama_model():
    """Test if llama3.2 model is available"""
    print(f"{Fore.CYAN}Checking for llama3.2 model...", end="", flush=True)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
        
        model_found = any('llama3.2' in model.get('name', '') for model in models)
        
        if model_found:
            print(f"{Fore.GREEN} ✓ Found")
            return True
        else:
            print(f"{Fore.RED} ✗ Not found")
            print(f"{Fore.YELLOW}  Install with: ollama pull llama3.2")
            
            if models:
                print(f"\n{Fore.CYAN}  Available models:")
                for model in models:
                    print(f"    - {model.get('name')}")
            
            return False
            
    except Exception as e:
        print(f"{Fore.RED} ✗ Error: {e}")
        return False


def test_llm_query():
    """Test a simple query to the LLM"""
    print(f"{Fore.CYAN}Testing LLM query...", end="", flush=True)
    
    try:
        payload = {
            "model": "llama3.2",
            "prompt": "Return JSON: {\"status\": \"ready\", \"test\": true}",
            "stream": False,
            "format": "json"
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get('response'):
            print(f"{Fore.GREEN} ✓ LLM responding")
            return True
        else:
            print(f"{Fore.YELLOW} ⚠ Unexpected response")
            return False
        
    except requests.exceptions.Timeout:
        print(f"{Fore.RED} ✗ Timeout")
        print(f"{Fore.YELLOW}  LLM is slow to respond (this is normal on first run)")
        return False
    except Exception as e:
        print(f"{Fore.RED} ✗ Error: {e}")
        return False


def test_dependencies():
    """Test if required Python packages are installed"""
    print(f"{Fore.CYAN}Checking dependencies...", end="", flush=True)
    
    required = ['requests', 'colorama']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        print(f"{Fore.GREEN} ✓ All installed")
        return True
    else:
        print(f"{Fore.RED} ✗ Missing: {', '.join(missing)}")
        print(f"{Fore.YELLOW}  Install with: pip install -r requirements.txt")
        return False


def main():
    """Main test entry point"""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 70)
    print("Communication Scanner - Setup Test")
    print("=" * 70)
    print(f"{Style.RESET_ALL}\n")
    
    results = []
    
    # Run all tests
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Ollama Connection", test_ollama_connection()))
    
    if results[-1][1]:  # If Ollama connected
        results.append(("Llama 3.2 Model", test_llama_model()))
        
        if results[-1][1]:  # If model found
            results.append(("LLM Query", test_llm_query()))
    
    # Summary
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}Test Summary")
    print(f"{Fore.CYAN}{'=' * 70}\n")
    
    for test_name, passed in results:
        status = f"{Fore.GREEN}✓ PASS" if passed else f"{Fore.RED}✗ FAIL"
        print(f"{status}{Fore.WHITE} - {test_name}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ All tests passed!")
        print(f"{Fore.GREEN}Your setup is ready to use.")
        print(f"\n{Fore.CYAN}Next steps:")
        print(f"{Fore.WHITE}  1. Edit config/config.json with your email credentials")
        print(f"{Fore.WHITE}  2. Run: python3 src/scanner.py")
        return 0
    else:
        print(f"{Fore.RED}{Style.BRIGHT}✗ Some tests failed")
        print(f"{Fore.YELLOW}Please fix the issues above and try again.")
        
        failed_tests = [name for name, passed in results if not passed]
        print(f"\n{Fore.RED}Failed: {', '.join(failed_tests)}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

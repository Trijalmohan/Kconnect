#!/bin/bash
echo "=========================================="
echo "Communication Scanner - Code Verification"
echo "=========================================="
echo ""

errors=0

echo "1. Checking Python syntax..."
python3 -m py_compile src/scanner.py 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ scanner.py syntax valid"
else
    echo "   ✗ scanner.py has syntax errors"
    errors=$((errors + 1))
fi

python3 -m py_compile test_setup.py 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ test_setup.py syntax valid"
else
    echo "   ✗ test_setup.py has syntax errors"
    errors=$((errors + 1))
fi

echo ""
echo "2. Checking JSON syntax..."
python3 -c "import json; json.load(open('config/config.json'))" 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ config.json valid"
else
    echo "   ✗ config.json invalid"
    errors=$((errors + 1))
fi

python3 -c "import json; json.load(open('config/config.example.json'))" 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ config.example.json valid"
else
    echo "   ✗ config.example.json invalid"
    errors=$((errors + 1))
fi

echo ""
echo "3. Checking imports..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from scanner import OllamaLLM, EmailScanner, CommunicationScanner
" 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ All imports successful"
else
    echo "   ✗ Import errors detected"
    errors=$((errors + 1))
fi

echo ""
echo "4. Checking file structure..."
required_files=(
    "src/scanner.py"
    "test_setup.py"
    "requirements.txt"
    "config/config.json"
    "config/config.example.json"
    "README.md"
    "QUICKSTART.md"
    ".gitignore"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file missing"
        errors=$((errors + 1))
    fi
done

echo ""
echo "5. Checking directories..."
required_dirs=(
    "src"
    "config"
    "data/results"
    "logs"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir/ exists"
    else
        echo "   ✗ $dir/ missing"
        errors=$((errors + 1))
    fi
done

echo ""
echo "=========================================="
if [ $errors -eq 0 ]; then
    echo "✓ ALL VERIFICATIONS PASSED"
    echo "=========================================="
    echo ""
    echo "Ready to use! Next steps:"
    echo "1. Edit config/config.json"
    echo "2. Run: python3 test_setup.py"
    echo "3. Run: python3 src/scanner.py"
    exit 0
else
    echo "✗ $errors VERIFICATION(S) FAILED"
    echo "=========================================="
    exit 1
fi

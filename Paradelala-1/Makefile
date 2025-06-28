.PHONY: help install test clean run-agents setup

help:
@echo "Available commands:"
@echo "  make install    - Install Python dependencies"
@echo "  make test       - Run tests"
@echo "  make clean      - Clean temporary files"
@echo "  make run-agents - Run AI agents for system analysis"
@echo "  make setup      - Run the complete setup"

install:
pip install -r requirements.txt

test:
python test_setup.py

clean:
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
rm -f /tmp/network_scan.json /tmp/system_analysis.json /tmp/security_audit.json /tmp/user_config.json

run-agents:
@echo "Running network scanner..."
python agents/network_scanner.py
@echo "\nRunning system analyzer..."
python agents/system_analyzer.py
@echo "\nRunning security auditor..."
python agents/security_auditor.py

setup:
sudo bash scripts/install.sh

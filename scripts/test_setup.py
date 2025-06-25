#!/usr/bin/env python3
"""
Test script to verify the home-lab setup components
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from agents.network_scanner import NetworkScanner
        print("✓ NetworkScanner imported")
        
        from agents.system_analyzer import SystemAnalyzer
        print("✓ SystemAnalyzer imported")
        
        from agents.security_auditor import SecurityAuditor
        print("✓ SecurityAuditor imported")
        
        from src.installer.questionnaire import Questionnaire
        print("✓ Questionnaire imported")
        
        from src.installer.configurator import Configurator
        print("✓ Configurator imported")
        
        from src.orchestrator import HomelabOrchestrator
        print("✓ HomelabOrchestrator imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_agents():
    """Test that agents can run basic operations"""
    print("\nTesting agents...")
    
    # Test NetworkScanner
    try:
        from agents.network_scanner import NetworkScanner
        scanner = NetworkScanner()
        # Just test initialization
        print("✓ NetworkScanner initialized")
    except Exception as e:
        print(f"✗ NetworkScanner failed: {e}")
    
    # Test SystemAnalyzer
    try:
        from agents.system_analyzer import SystemAnalyzer
        analyzer = SystemAnalyzer()
        # Test basic system info
        info = analyzer.get_system_info()
        print(f"✓ SystemAnalyzer working - OS: {info.get('system', 'Unknown')}")
    except Exception as e:
        print(f"✗ SystemAnalyzer failed: {e}")
    
    # Test SecurityAuditor
    try:
        from agents.security_auditor import SecurityAuditor
        auditor = SecurityAuditor()
        print("✓ SecurityAuditor initialized")
    except Exception as e:
        print(f"✗ SecurityAuditor failed: {e}")

def test_configuration_flow():
    """Test the configuration generation flow"""
    print("\nTesting configuration flow...")
    
    # Create a test user config
    test_config = {
        "timestamp": "2024-01-01T00:00:00",
        "basic_info": {
            "project_name": "test-homelab",
            "domain": "",
            "environment": "development"
        },
        "services": {
            "docker": True,
            "docker_compose": True,
            "nginx": True,
            "prometheus": True,
            "grafana": True
        },
        "security": {
            "ssh_port": 22,
            "disable_password_auth": False,
            "enable_firewall": True,
            "enable_fail2ban": True,
            "auto_updates": True
        },
        "networking": {
            "docker_subnet": "172.20.0.0/16"
        },
        "monitoring": {
            "retention_days": 30
        }
    }
    
    # Save test config
    with open('/tmp/user_config.json', 'w') as f:
        json.dump(test_config, f, indent=2)
    print("✓ Test configuration created")
    
    # Test configurator
    try:
        from src.installer.configurator import Configurator
        configurator = Configurator()
        print("✓ Configurator loaded test config")
        
        # Test docker-compose generation
        compose_content = configurator.generate_docker_compose()
        if 'version:' in compose_content and 'services:' in compose_content:
            print("✓ Docker Compose generation working")
        else:
            print("✗ Docker Compose generation failed")
            
    except Exception as e:
        print(f"✗ Configurator failed: {e}")

def test_file_structure():
    """Test that all required files exist"""
    print("\nChecking file structure...")
    
    required_files = [
        'README.md',
        'scripts/install.sh',
        'agents/network_scanner.py',
        'agents/system_analyzer.py',
        'agents/security_auditor.py',
        'src/installer/questionnaire.py',
        'src/installer/configurator.py',
        'src/orchestrator.py'
    ]
    
    project_root = Path(__file__).parent.parent
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")

def main():
    """Run all tests"""
    print("=== Home Lab Setup Component Test ===\n")
    
    # Run tests
    test_file_structure()
    
    if test_imports():
        test_agents()
        test_configuration_flow()
    
    print("\n=== Test Complete ===")
    print("\nIf all tests passed, you can run the installer with:")
    print("  sudo bash scripts/install.sh")

if __name__ == "__main__":
    main()

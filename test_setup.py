#!/usr/bin/env python3
"""
Test script to verify the secure home-lab setup
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (not found)")
        return False

def check_directory_structure():
    """Check if all required directories exist"""
    print("\n🔍 Checking directory structure...")
    
    directories = {
        "src": "Source code directory",
        "agents": "AI agents directory",
        "security": "Security configurations",
        "config": "Configuration templates",
        "scripts": "Installation scripts",
        "docs": "Documentation",
        "tests": "Test suites"
    }
    
    all_exist = True
    for dir_name, description in directories.items():
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {description}: {dir_name}/")
        else:
            print(f"❌ {description}: {dir_name}/ (not found)")
            all_exist = False
    
    return all_exist

def check_core_files():
    """Check if core files exist"""
    print("\n🔍 Checking core files...")
    
    files = {
        "scripts/install.sh": "Main installation script",
        "requirements.txt": "Python dependencies",
        "README.md": "Project documentation",
        ".env.example": "Environment variables example",
        "agents/network_scanner.py": "Network scanner agent",
        "agents/system_analyzer.py": "System analyzer agent",
        "agents/security_auditor.py": "Security auditor agent",
        "src/installer/questionnaire.py": "Interactive questionnaire",
        "src/installer/configurator.py": "Configuration generator"
    }
    
    all_exist = True
    for filepath, description in files.items():
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_python_imports():
    """Check if required Python modules can be imported"""
    print("\n🔍 Checking Python imports...")
    
    modules = [
        "click",
        "yaml",
        "jinja2",
        "requests",
        "psutil",
        "netifaces"
    ]
    
    all_imported = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ Module '{module}' can be imported")
        except ImportError:
            print(f"❌ Module '{module}' not found (install with: pip install {module})")
            all_imported = False
    
    return all_imported

def main():
    """Run all checks"""
    print("=" * 60)
    print("🚀 Secure Home-Lab Setup Verification")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run checks
    dir_check = check_directory_structure()
    file_check = check_core_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    if dir_check and file_check:
        print("✅ All checks passed! The setup is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure it")
        print("2. Run: sudo bash scripts/install.sh")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

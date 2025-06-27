#!/usr/bin/env python3
"""
Test script to verify the Homelab Builder components work correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from agents.environment_scanner import EnvironmentScanner
        print("✓ Environment Scanner imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Environment Scanner: {e}")
    
    try:
        from agents.network_analyzer import NetworkAnalyzer
        print("✓ Network Analyzer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Network Analyzer: {e}")
    
    try:
        from agents.service_recommender import ServiceRecommender
        print("✓ Service Recommender imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Service Recommender: {e}")
    
    try:
        from installer.survey import UserSurvey
        print("✓ User Survey imported successfully")
    except Exception as e:
        print(f"✗ Failed to import User Survey: {e}")
    
    try:
        from deployment.deployer import ServiceDeployer
        print("✓ Service Deployer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Service Deployer: {e}")
    
    try:
        from proxy.tunnel_manager import TunnelManager
        print("✓ Tunnel Manager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Tunnel Manager: {e}")
    
    try:
        from utils.config_manager import ConfigManager
        print("✓ Config Manager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Config Manager: {e}")
    
    try:
        from utils.logger import setup_logger
        print("✓ Logger imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Logger: {e}")

def test_basic_functionality():
    """Test basic functionality of key components."""
    print("\nTesting basic functionality...")
    
    try:
        from agents.environment_scanner import EnvironmentScanner
        scanner = EnvironmentScanner()
        print("✓ Environment Scanner instantiated successfully")
    except Exception as e:
        print(f"✗ Failed to instantiate Environment Scanner: {e}")
    
    try:
        from agents.service_recommender import ServiceRecommender
        recommender = ServiceRecommender()
        catalog = recommender.service_catalog
        print(f"✓ Service Recommender loaded {len(catalog)} services")
    except Exception as e:
        print(f"✗ Failed to load service catalog: {e}")
    
    try:
        from utils.config_manager import ConfigManager
        config_mgr = ConfigManager()
        print("✓ Config Manager instantiated successfully")
    except Exception as e:
        print(f"✗ Failed to instantiate Config Manager: {e}")

if __name__ == "__main__":
    print("=== Homelab Builder Component Test ===\n")
    test_imports()
    test_basic_functionality()
    print("\n=== Test Complete ===")

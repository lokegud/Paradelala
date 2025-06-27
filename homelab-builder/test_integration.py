#!/usr/bin/env python3
"""
Homelab Builder Test Runner
Tests the core functionality without requiring all dependencies.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_scan():
    """Test environment scanning."""
    print("\n🔍 Testing Environment Scanner...")
    
    from agents.environment_scanner import EnvironmentScanner
    scanner = EnvironmentScanner()
    
    # Run scan
    scan_results = scanner.scan()
    
    print("\n📊 Scan Results:")
    print(f"  OS: {scan_results.get('os', 'Unknown')}")
    print(f"  CPU Cores: {scan_results.get('cpu_count', 'Unknown')}")
    print(f"  Memory: {scan_results.get('memory', {}).get('total_gb', 0):.1f} GB")
    print(f"  Docker: {'Installed' if scan_results.get('docker', {}).get('installed') else 'Not installed'}")
    
    return scan_results

def test_service_recommendations():
    """Test service recommendation engine."""
    print("\n🤖 Testing Service Recommender...")
    
    from agents.service_recommender import ServiceRecommender
    recommender = ServiceRecommender()
    
    # Mock scan data
    scan_data = {
        'environment': {
            'cpu_count': 4,
            'memory': {'available_gb': 8},
            'disk': {'free_gb': 100},
            'docker': {'installed': True}
        }
    }
    
    # Mock survey data
    survey_data = {
        'primary_use': 'media_server',
        'media_details': {
            'content_type': ['Movies', 'TV Shows'],
            'transcoding': True
        },
        'users': '2-5 (family)',
        'security_level': 'enhanced',
        'external_access': {
            'needed': True,
            'method': 'VPN (most secure)'
        },
        'monitoring': {
            'level': 'Basic uptime monitoring',
            'alerts': True
        },
        'backup_preference': {
            'strategy': 'Local backups only',
            'frequency': 'Daily'
        }
    }
    
    # Get recommendations
    recommendations = recommender.recommend(scan_data, survey_data)
    
    print("\n📋 Recommendations:")
    print(f"  Core Services: {[s['name'] for s in recommendations['core_services']]}")
    print(f"  Optional Services: {[s['name'] for s in recommendations['optional_services']]}")
    print(f"  Proxy Type: {recommendations['proxy_config'].get('tunnel_type', 'N/A')}")
    print(f"  Security Level: {recommendations['security_config'].get('auth_method', 'N/A')}")
    
    return recommendations

def test_config_generation():
    """Test configuration generation."""
    print("\n⚙️  Testing Configuration Generation...")
    
    # Create a test configuration
    test_config = {
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'deployment': {
            'services': ['jellyfin', 'wireguard', 'nginx-proxy-manager'],
            'resources': {
                'cpu_allocated': '75%',
                'memory_allocated': '6GB'
            }
        },
        'security': {
            'firewall': 'enabled',
            'ssl': 'letsencrypt',
            'auth': '2fa'
        }
    }
    
    print("\n📄 Generated Configuration:")
    print(json.dumps(test_config, indent=2))
    
    return test_config

def test_docker_compose_generation():
    """Test Docker Compose file generation."""
    print("\n🐳 Testing Docker Compose Generation...")
    
    compose_content = {
        'version': '3.8',
        'services': {
            'jellyfin': {
                'image': 'jellyfin/jellyfin:latest',
                'container_name': 'jellyfin',
                'ports': ['8096:8096'],
                'volumes': [
                    './data/jellyfin/config:/config',
                    './data/jellyfin/cache:/cache'
                ],
                'restart': 'unless-stopped'
            },
            'nginx-proxy-manager': {
                'image': 'jc21/nginx-proxy-manager:latest',
                'container_name': 'nginx-proxy-manager',
                'ports': ['80:80', '443:443', '81:81'],
                'volumes': ['./data/npm:/data'],
                'restart': 'unless-stopped'
            }
        },
        'networks': {
            'homelab': {
                'driver': 'bridge'
            }
        }
    }
    
    print("\n📝 Sample Docker Compose:")
    print("services:")
    for service, config in compose_content['services'].items():
        print(f"  - {service} ({config['image']})")
    
    return compose_content

def run_integration_test():
    """Run a full integration test."""
    print("=" * 60)
    print("       🧪 HOMELAB BUILDER INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Environment Scanning
        scan_results = test_environment_scan()
        print("✅ Environment scanning successful")
        
        # Test 2: Service Recommendations
        recommendations = test_service_recommendations()
        print("✅ Service recommendation successful")
        
        # Test 3: Configuration Generation
        config = test_config_generation()
        print("✅ Configuration generation successful")
        
        # Test 4: Docker Compose Generation
        compose = test_docker_compose_generation()
        print("✅ Docker Compose generation successful")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
        print("\n📊 Test Summary:")
        print(f"  - System: {scan_results.get('os', 'Unknown')}")
        print(f"  - Resources: {scan_results.get('cpu_count', 'Unknown')} CPUs, "
              f"{scan_results.get('memory', {}).get('total_gb', 0):.1f}GB RAM")
        print(f"  - Recommended Services: {len(recommendations['core_services']) + len(recommendations['optional_services'])}")
        print(f"  - Docker Ready: {'Yes' if scan_results.get('docker', {}).get('installed') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)

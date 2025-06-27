#!/usr/bin/env python3
"""
Homelab Builder Demo
Shows the structure and capabilities without requiring all dependencies.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_service_catalog():
    """Display available services."""
    from agents.service_recommender import ServiceRecommender
    
    print("\n📦 Available Services in Catalog:\n")
    
    recommender = ServiceRecommender()
    catalog = recommender.service_catalog
    
    # Group services by category
    categories = {}
    for service_id, service in catalog.items():
        category = service['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(service)
    
    # Display by category
    for category, services in sorted(categories.items()):
        print(f"\n{category.upper()}:")
        print("-" * 40)
        for service in services:
            print(f"  • {service['name']:<20} - {service['purpose']}")
            print(f"    Resources: CPU: {service['resources']['cpu']}, "
                  f"RAM: {service['resources']['memory']}, "
                  f"Disk: {service['resources']['disk']}")
            print(f"    Difficulty: {service['difficulty']}")

def show_architecture():
    """Display the system architecture."""
    print("\n🏗️  System Architecture:\n")
    
    architecture = """
    ┌─────────────────────────────────────────────────────────┐
    │                   HOMELAB BUILDER                       │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
    │  │ Environment │  │   Network    │  │    Service    │ │
    │  │   Scanner   │  │   Analyzer   │  │  Recommender  │ │
    │  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘ │
    │         │                 │                   │         │
    │         └─────────────────┴───────────────────┘         │
    │                           │                             │
    │                    ┌──────┴──────┐                      │
    │                    │   Survey    │                      │
    │                    │   Module    │                      │
    │                    └──────┬──────┘                      │
    │                           │                             │
    │                    ┌──────┴──────┐                      │
    │                    │  Deployment │                      │
    │                    │   Engine    │                      │
    │                    └──────┬──────┘                      │
    │                           │                             │
    │         ┌─────────────────┴───────────────────┐         │
    │         │                                     │         │
    │  ┌──────┴──────┐  ┌──────────────┐  ┌───────┴───────┐ │
    │  │   Docker    │  │    Tunnel    │  │   Monitoring  │ │
    │  │   Compose   │  │   Manager    │  │    Setup      │ │
    │  └─────────────┘  └──────────────┘  └───────────────┘ │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    """
    print(architecture)

def show_sample_config():
    """Show a sample configuration."""
    print("\n📋 Sample Configuration Output:\n")
    
    sample_config = {
        "scan_results": {
            "environment": {
                "os": "Ubuntu 22.04",
                "cpu_cores": 4,
                "memory_gb": 8,
                "disk_free_gb": 100,
                "docker_installed": True
            },
            "network": {
                "public_ip": "203.0.113.1",
                "private_ip": "192.168.1.100",
                "firewall_active": True,
                "open_ports": [22, 80, 443]
            }
        },
        "user_preferences": {
            "primary_use": "media_server",
            "users": "2-5 (family)",
            "security_level": "enhanced",
            "external_access": {
                "needed": True,
                "method": "VPN (most secure)"
            }
        },
        "recommendations": {
            "core_services": ["Jellyfin", "WireGuard", "Nginx Proxy Manager"],
            "optional_services": ["Uptime Kuma", "Duplicati"],
            "estimated_resources": {
                "cpu_usage": "50%",
                "memory_usage": "4GB",
                "disk_usage": "20GB"
            }
        }
    }
    
    print(json.dumps(sample_config, indent=2))

def show_deployment_example():
    """Show deployment example."""
    print("\n🚀 Example Docker Compose Output:\n")
    
    compose_example = """version: '3.8'

services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=UTC
    volumes:
      - ./data/jellyfin/config:/config
      - ./data/jellyfin/cache:/cache
      - /media:/media:ro
    ports:
      - 8096:8096
    restart: unless-stopped
    networks:
      - homelab

  nginx-proxy-manager:
    image: jc21/nginx-proxy-manager:latest
    container_name: nginx-proxy-manager
    ports:
      - 80:80
      - 443:443
      - 81:81
    volumes:
      - ./data/npm/data:/data
      - ./data/npm/letsencrypt:/etc/letsencrypt
    restart: unless-stopped
    networks:
      - homelab

networks:
  homelab:
    driver: bridge
"""
    print(compose_example)

def main():
    print("=" * 60)
    print("          🏠 HOMELAB BUILDER DEMO")
    print("=" * 60)
    
    print("\nThis demo shows the capabilities of the Homelab Builder")
    print("without requiring all dependencies to be installed.\n")
    
    # Show architecture
    show_architecture()
    
    # Show service catalog
    show_service_catalog()
    
    # Show sample configuration
    show_sample_config()
    
    # Show deployment example
    show_deployment_example()
    
    print("\n" + "=" * 60)
    print("\nTo run the full installer with all features:")
    print("  1. Install dependencies: ./install.sh")
    print("  2. Or manually: pip install -r requirements.txt")
    print("  3. Run: python installer/main.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

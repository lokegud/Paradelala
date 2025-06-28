#!/usr/bin/env python3
"""
Docker Compose Generator
Generates docker-compose.yml from user configuration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from installer.configurator import Configurator


def main():
    """Main entry point"""
    configurator = Configurator()
    
    # Only generate docker-compose.yml
    configurator.generate_docker_compose()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

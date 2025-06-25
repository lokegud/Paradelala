#!/usr/bin/env python3
"""
Main Orchestrator for Secure Home-Lab Setup
Coordinates all components and provides a unified interface
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.network_scanner import NetworkScanner
from agents.system_analyzer import SystemAnalyzer
from agents.security_auditor import SecurityAuditor
from src.installer.questionnaire import Questionnaire
from src.installer.configurator import Configurator

class HomelabOrchestrator:
    """Main orchestrator for home-lab setup"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.setup_logging()
        self.results = {
            'network_scan': None,
            'system_analysis': None,
            'security_audit': None,
            'user_config': None,
            'deployment_path': None
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/tmp/homelab_setup.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('HomelabOrchestrator')
    
    def print_banner(self):
        """Print welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                  Secure Home-Lab Setup v1.0                   ║
║                                                               ║
║  AI-Powered Infrastructure Deployment for Your Home Lab       ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def run_system_analysis(self) -> Dict[str, Any]:
        """Run all system analysis agents"""
        self.logger.info("Starting system analysis phase...")
        
        # Network Scanner
        print("\n[1/3] Running network scanner...")
        try:
            scanner = NetworkScanner()
            self.results['network_scan'] = scanner.run_full_scan()
            with open('/tmp/network_scan.json', 'w') as f:
                json.dump(self.results['network_scan'], f, indent=2)
            print("✓ Network scan completed")
        except Exception as e:
            self.logger.error(f"Network scan failed: {str(e)}")
            print(f"✗ Network scan failed: {str(e)}")
        
        # System Analyzer
        print("\n[2/3] Running system analyzer...")
        try:
            analyzer = SystemAnalyzer()
            self.results['system_analysis'] = analyzer.run_full_analysis()
            with open('/tmp/system_analysis.json', 'w') as f:
                json.dump(self.results['system_analysis'], f, indent=2)
            print("✓ System analysis completed")
        except Exception as e:
            self.logger.error(f"System analysis failed: {str(e)}")
            print(f"✗ System analysis failed: {str(e)}")
        
        # Security Auditor
        print("\n[3/3] Running security auditor...")
        try:
            auditor = SecurityAuditor()
            self.results['security_audit'] = auditor.run_full_audit()
            with open('/tmp/security_audit.json', 'w') as f:
                json.dump(self.results['security_audit'], f, indent=2)
            print("✓ Security audit completed")
        except Exception as e:
            self.logger.error(f"Security audit failed: {str(e)}")
            print(f"✗ Security audit failed: {str(e)}")
        
        return self.results
    
    def display_analysis_summary(self):
        """Display summary of system analysis"""
        print("\n" + "="*60)
        print("SYSTEM ANALYSIS SUMMARY")
        print("="*60)
        
        # System Info
        if self.results['system_analysis']:
            sys_info = self.results['system_analysis'].get('system_info', {})
            hardware = self.results['system_analysis'].get('hardware', {})
            capabilities = self.results['system_analysis'].get('capabilities', {})
            
            print(f"\nSystem: {sys_info.get('system', 'Unknown')} {sys_info.get('release', '')}")
            print(f"CPU: {hardware.get('cpu', {}).get('brand', 'Unknown')}")
            print(f"Cores: {hardware.get('cpu', {}).get('cores', 'Unknown')}")
            print(f"RAM: {hardware.get('memory', {}).get('total', 'Unknown')}")
            print(f"Performance Rating: {capabilities.get('performance_rating', 'Unknown')}")
        
        # Network Info
        if self.results['network_scan']:
            print(f"\nExternal IP: {self.results['network_scan'].get('external_ip', 'Unknown')}")
            topology = self.results['network_scan'].get('network_topology', {})
            print(f"Network Type: {topology.get('network_type', 'Unknown')}")
            print(f"NAT Detected: {topology.get('nat_detected', False)}")
        
        # Security Info
        if self.results['security_audit']:
            print(f"\nSecurity Score: {self.results['security_audit'].get('security_score', 0)}/100")
            print(f"Risk Level: {self.results['security_audit'].get('risk_level', 'Unknown')}")
            
            # Top recommendations
            recommendations = self.results['security_audit'].get('recommendations', [])
            if recommendations:
                print("\nTop Security Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {rec}")
        
        print("\n" + "="*60)
    
    def run_questionnaire(self):
        """Run interactive questionnaire"""
        self.logger.info("Starting questionnaire...")
        
        # Check if running in non-interactive mode
        if hasattr(sys, '_called_from_test') or not sys.stdin.isatty():
            self.logger.info("Running in non-interactive mode, using defaults")
            subprocess.run([sys.executable, 'src/installer/questionnaire.py', '--non-interactive'])
        else:
            questionnaire = Questionnaire()
            questionnaire.run()
        
        # Load the generated config
        with open('/tmp/user_config.json', 'r') as f:
            self.results['user_config'] = json.load(f)
    
    def generate_configurations(self):
        """Generate all configuration files"""
        self.logger.info("Generating configurations...")
        
        configurator = Configurator()
        self.results['deployment_path'] = configurator.generate_all_configs()
        
        return self.results['deployment_path']
    
    def apply_security_hardening(self):
        """Apply security hardening based on audit results"""
        print("\nApplying security hardening...")
        
        hardening_tasks = []
        
        # Check firewall
        if self.results['security_audit']:
            network_security = self.results['security_audit'].get('network_security', {})
            if network_security.get('firewall_status') in ['unknown', 'ufw_inactive']:
                hardening_tasks.append({
                    'name': 'Enable UFW firewall',
                    'commands': [
                        'ufw --force enable',
                        'ufw default deny incoming',
                        'ufw default allow outgoing',
                        'ufw allow ssh',
                        'ufw allow 80/tcp',
                        'ufw allow 443/tcp'
                    ]
                })
        
        # Apply hardening tasks
        for task in hardening_tasks:
            print(f"  - {task['name']}")
            for cmd in task['commands']:
                try:
                    subprocess.run(cmd.split(), check=True, capture_output=True)
                except Exception as e:
                    self.logger.warning(f"Failed to execute: {cmd} - {str(e)}")
        
        print("✓ Security hardening completed")
    
    def create_deployment_scripts(self):
        """Create additional deployment and management scripts"""
        if not self.results['deployment_path']:
            return
        
        scripts_dir = os.path.join(self.results['deployment_path'], 'scripts')
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Backup script
        backup_script = """#!/bin/bash
# Backup script for Home Lab

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/homelab_backup_$TIMESTAMP.tar.gz"

mkdir -p $BACKUP_DIR

echo "Starting backup..."

# Stop services
docker-compose down

# Backup data directory
tar -czf $BACKUP_FILE ./data ./config .env

# Restart services
docker-compose up -d

echo "Backup completed: $BACKUP_FILE"
"""
        
        with open(os.path.join(scripts_dir, 'backup.sh'), 'w') as f:
            f.write(backup_script)
        os.chmod(os.path.join(scripts_dir, 'backup.sh'), 0o755)
        
        # Update script
        update_script = """#!/bin/bash
# Update script for Home Lab

echo "Updating Home Lab services..."

# Pull latest images
docker-compose pull

# Restart services with new images
docker-compose up -d

# Prune old images
docker image prune -f

echo "Update completed!"
"""
        
        with open(os.path.join(scripts_dir, 'update.sh'), 'w') as f:
            f.write(update_script)
        os.chmod(os.path.join(scripts_dir, 'update.sh'), 0o755)
        
        # Status script
        status_script = """#!/bin/bash
# Status script for Home Lab

echo "=== Home Lab Status ==="
echo

echo "Container Status:"
docker-compose ps

echo
echo "Resource Usage:"
docker stats --no-stream

echo
echo "Disk Usage:"
df -h | grep -E "^/dev|Filesystem"

echo
echo "Network Connections:"
netstat -tlnp 2>/dev/null | grep LISTEN || ss -tlnp | grep LISTEN
"""
        
        with open(os.path.join(scripts_dir, 'status.sh'), 'w') as f:
            f.write(status_script)
        os.chmod(os.path.join(scripts_dir, 'status.sh'), 0o755)
        
        self.logger.info("Created management scripts")
    
    def display_next_steps(self):
        """Display next steps for the user"""
        if not self.results['deployment_path']:
            return
        
        print("\n" + "="*60)
        print("DEPLOYMENT READY!")
        print("="*60)
        
        print(f"\nYour home-lab configuration has been generated at:")
        print(f"  {self.results['deployment_path']}")
        
        print("\nNext steps:")
        print("1. Review the configuration files:")
        print(f"   cd {self.results['deployment_path']}")
        print("   cat docker-compose.yml")
        print("   cat .env  # Contains passwords - keep secure!")
        
        print("\n2. Deploy your home-lab:")
        print("   ./deploy.sh")
        
        print("\n3. Check service status:")
        print("   docker-compose ps")
        print("   ./scripts/status.sh")
        
        if self.results['user_config'].get('basic_info', {}).get('domain'):
            domain = self.results['user_config']['basic_info']['domain']
            print(f"\n4. Access your services:")
            print(f"   Main: https://{domain}")
            if self.results['user_config'].get('services', {}).get('grafana'):
                print(f"   Grafana: https://grafana.{domain}")
            if self.results['user_config'].get('services', {}).get('prometheus'):
                print(f"   Prometheus: https://prometheus.{domain}")
        
        print("\n5. Backup your configuration:")
        print("   ./scripts/backup.sh")
        
        print("\n" + "="*60)
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("- Keep your .env file secure and never commit it to version control")
        print("- Review all generated configurations before deployment")
        print("- Set up regular backups of your data")
        print("- Monitor your services regularly")
        print("\n" + "="*60)
    
    def run(self, skip_analysis: bool = False, skip_questionnaire: bool = False):
        """Run the complete orchestration"""
        self.print_banner()
        
        try:
            # Phase 1: System Analysis
            if not skip_analysis:
                print("\n📊 Phase 1: System Analysis")
                print("-" * 40)
                self.run_system_analysis()
                self.display_analysis_summary()
            else:
                self.logger.info("Skipping system analysis")
            
            # Phase 2: User Configuration
            if not skip_questionnaire:
                print("\n⚙️  Phase 2: Configuration")
                print("-" * 40)
                self.run_questionnaire()
            else:
                self.logger.info("Skipping questionnaire")
            
            # Phase 3: Generate Configurations
            print("\n🔧 Phase 3: Generating Configurations")
            print("-" * 40)
            self.generate_configurations()
            
            # Phase 4: Security Hardening
            print("\n🔒 Phase 4: Security Hardening")
            print("-" * 40)
            self.apply_security_hardening()
            
            # Phase 5: Create Scripts
            print("\n📝 Phase 5: Creating Management Scripts")
            print("-" * 40)
            self.create_deployment_scripts()
            print("✓ Management scripts created")
            
            # Display next steps
            self.display_next_steps()
            
            self.logger.info("Orchestration completed successfully")
            
        except KeyboardInterrupt:
            print("\n\nSetup interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Orchestration failed: {str(e)}")
            print(f"\n❌ Setup failed: {str(e)}")
            sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Secure Home-Lab Setup Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete setup
  %(prog)s
  
  # Skip system analysis (use existing results)
  %(prog)s --skip-analysis
  
  # Skip questionnaire (use existing config)
  %(prog)s --skip-questionnaire
  
  # Verbose output
  %(prog)s --verbose
        """
    )
    
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='Skip system analysis phase (use existing results)'
    )
    
    parser.add_argument(
        '--skip-questionnaire',
        action='store_true',
        help='Skip questionnaire phase (use existing config)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator and run
    orchestrator = HomelabOrchestrator(verbose=args.verbose)
    orchestrator.run(
        skip_analysis=args.skip_analysis,
        skip_questionnaire=args.skip_questionnaire
    )


if __name__ == "__main__":
    main()

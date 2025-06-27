#!/usr/bin/env python3
"""
Homelab Builder - Main Interactive Installer
This module provides the main entry point for the interactive installation process.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint
import questionary
from questionary import Style

from agents.environment_scanner import EnvironmentScanner
from agents.network_analyzer import NetworkAnalyzer
from agents.service_recommender import ServiceRecommender
from installer.survey import UserSurvey
from deployment.deployer import ServiceDeployer
from proxy.tunnel_manager import TunnelManager
from utils.config_manager import ConfigManager
from utils.logger import setup_logger

# Setup console and logger
console = Console()
logger = setup_logger()

# Custom style for questionary
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


class HomelabInstaller:
    """Main installer class that orchestrates the installation process."""
    
    def __init__(self):
        self.console = console
        self.config_manager = ConfigManager()
        self.environment_scanner = EnvironmentScanner()
        self.network_analyzer = NetworkAnalyzer()
        self.service_recommender = ServiceRecommender()
        self.user_survey = UserSurvey()
        self.service_deployer = ServiceDeployer()
        self.tunnel_manager = TunnelManager()
        
    def display_welcome(self):
        """Display welcome message and introduction."""
        welcome_text = """
[bold cyan]Welcome to Homelab Builder![/bold cyan]

This intelligent installer will help you set up a secure and private home-lab
that can be deployed to a VPS and used as a proxy to your home server.

[yellow]What we'll do:[/yellow]
• Scan your environment and network
• Ask you about your use case and preferences
• Recommend the best services for your needs
• Deploy and configure everything automatically
• Set up secure tunneling to your home server

[green]Let's get started![/green]
        """
        
        panel = Panel(welcome_text.strip(), title="🏠 Homelab Builder", border_style="cyan")
        self.console.print(panel)
        
    def run_environment_scan(self) -> Dict[str, Any]:
        """Run environment and network scans."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Environment scan
            task1 = progress.add_task("[cyan]Scanning system environment...", total=None)
            env_data = self.environment_scanner.scan()
            progress.update(task1, completed=True)
            
            # Network scan
            task2 = progress.add_task("[cyan]Analyzing network configuration...", total=None)
            network_data = self.network_analyzer.analyze()
            progress.update(task2, completed=True)
            
        return {
            "environment": env_data,
            "network": network_data
        }
    
    def display_scan_results(self, scan_data: Dict[str, Any]):
        """Display the results of environment and network scans."""
        # Environment table
        env_table = Table(title="System Environment", show_header=True, header_style="bold magenta")
        env_table.add_column("Property", style="cyan", no_wrap=True)
        env_table.add_column("Value", style="green")
        
        env_data = scan_data["environment"]
        env_table.add_row("Operating System", f"{env_data['os_info']['system']} {env_data['os_info']['release']}")
        env_table.add_row("CPU Cores", str(env_data['cpu_count']))
        env_table.add_row("Total RAM", f"{env_data['memory']['total_gb']:.2f} GB")
        env_table.add_row("Available RAM", f"{env_data['memory']['available_gb']:.2f} GB")
        env_table.add_row("Disk Space", f"{env_data['disk']['free_gb']:.2f} GB free of {env_data['disk']['total_gb']:.2f} GB")
        env_table.add_row("Docker", "✓ Installed" if env_data['docker']['installed'] else "✗ Not installed")
        
        self.console.print(env_table)
        self.console.print()
        
        # Network table
        net_table = Table(title="Network Configuration", show_header=True, header_style="bold magenta")
        net_table.add_column("Property", style="cyan", no_wrap=True)
        net_table.add_column("Value", style="green")
        
        net_data = scan_data["network"]
        net_table.add_row("Public IP", net_data.get('public_ip', 'Unknown'))
        net_table.add_row("Primary Interface", net_data.get('primary_interface', 'Unknown'))
        net_table.add_row("Open Ports", ", ".join(map(str, net_data.get('open_ports', []))))
        net_table.add_row("Firewall", "Active" if net_data.get('firewall_active') else "Inactive")
        
        self.console.print(net_table)
        self.console.print()
    
    def run_user_survey(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the interactive user survey."""
        self.console.print("[bold cyan]Now let's learn about your needs...[/bold cyan]\n")
        return self.user_survey.conduct_survey(scan_data)
    
    def get_service_recommendations(self, scan_data: Dict[str, Any], survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered service recommendations."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing requirements and generating recommendations...", total=None)
            recommendations = self.service_recommender.recommend(scan_data, survey_data)
            progress.update(task, completed=True)
            
        return recommendations
    
    def display_recommendations(self, recommendations: Dict[str, Any]) -> bool:
        """Display service recommendations and get user confirmation."""
        self.console.print("\n[bold cyan]Based on your requirements, here's what we recommend:[/bold cyan]\n")
        
        # Core services
        core_table = Table(title="Core Services", show_header=True, header_style="bold magenta")
        core_table.add_column("Service", style="cyan", no_wrap=True)
        core_table.add_column("Purpose", style="green")
        core_table.add_column("Resources", style="yellow")
        
        for service in recommendations['core_services']:
            core_table.add_row(
                service['name'],
                service['purpose'],
                f"CPU: {service['resources']['cpu']}, RAM: {service['resources']['memory']}"
            )
        
        self.console.print(core_table)
        self.console.print()
        
        # Optional services
        if recommendations.get('optional_services'):
            opt_table = Table(title="Optional Services", show_header=True, header_style="bold magenta")
            opt_table.add_column("Service", style="cyan", no_wrap=True)
            opt_table.add_column("Purpose", style="green")
            opt_table.add_column("Resources", style="yellow")
            
            for service in recommendations['optional_services']:
                opt_table.add_row(
                    service['name'],
                    service['purpose'],
                    f"CPU: {service['resources']['cpu']}, RAM: {service['resources']['memory']}"
                )
            
            self.console.print(opt_table)
            self.console.print()
        
        # Configuration summary
        config_text = f"""[bold]Configuration Summary:[/bold]
            
• Proxy Type: {recommendations['proxy_config']['type']}
• SSL/TLS: {recommendations['proxy_config']['ssl_provider']}
• Authentication: {recommendations['security_config']['auth_method']}
• Firewall: {recommendations['security_config']['firewall']}
• Backup Strategy: {recommendations['backup_config']['strategy']}
• Monitoring: {recommendations['monitoring_config']['solution']}"""
        
        config_panel = Panel(
            config_text,
            title="📋 Deployment Plan",
            border_style="green"
        )
        self.console.print(config_panel)
        
        # Get user confirmation
        return questionary.confirm(
            "Do you want to proceed with this configuration?",
            default=True,
            style=custom_style
        ).ask()
    
    def deploy_services(self, recommendations: Dict[str, Any], scan_data: Dict[str, Any]):
        """Deploy and configure all services."""
        self.console.print("\n[bold green]Starting deployment process...[/bold green]\n")
        
        # Save configuration
        config_path = self.config_manager.save_config({
            'scan_data': scan_data,
            'recommendations': recommendations,
            'timestamp': time.time()
        })
        
        # Deploy services
        deployment_result = self.service_deployer.deploy(recommendations, config_path)
        
        if deployment_result['success']:
            self.console.print("[bold green]✓ All services deployed successfully![/bold green]")
            
            # Setup tunnel/proxy
            self.console.print("\n[bold cyan]Setting up secure tunnel...[/bold cyan]")
            tunnel_result = self.tunnel_manager.setup(recommendations['proxy_config'])
            
            if tunnel_result['success']:
                self.display_completion(deployment_result, tunnel_result)
            else:
                self.console.print(f"[bold red]✗ Tunnel setup failed: {tunnel_result['error']}[/bold red]")
        else:
            self.console.print(f"[bold red]✗ Deployment failed: {deployment_result['error']}[/bold red]")
    
    def display_completion(self, deployment_result: Dict[str, Any], tunnel_result: Dict[str, Any]):
        """Display completion message with access information."""
        completion_text = f"""[bold green]🎉 Congratulations! Your Homelab is ready![/bold green]
        
[bold]Access Information:[/bold]
• Dashboard URL: {deployment_result['dashboard_url']}
• Admin Username: admin
• Admin Password: {deployment_result['admin_password']}

[bold]Tunnel Configuration:[/bold]
• VPN Config: {tunnel_result['vpn_config_path']}
• Public Endpoint: {tunnel_result['public_endpoint']}

[bold]Next Steps:[/bold]
1. Access your dashboard at the URL above
2. Configure your home server to connect via the VPN
3. Set up any additional services through the dashboard

[yellow]Important:[/yellow] Save your admin password in a secure location!

Configuration saved to: {deployment_result['config_path']}"""
        
        panel = Panel(completion_text, title="✅ Installation Complete", border_style="green")
        self.console.print(panel)
    
    def run(self):
        """Main installation flow."""
        try:
            # Welcome
            self.display_welcome()
            
            if not questionary.confirm(
                "Ready to begin the installation?",
                default=True,
                style=custom_style
            ).ask():
                self.console.print("[yellow]Installation cancelled.[/yellow]")
                return
            
            # Environment scan
            self.console.print("\n[bold cyan]Step 1: Environment Analysis[/bold cyan]\n")
            scan_data = self.run_environment_scan()
            self.display_scan_results(scan_data)
            
            # User survey
            self.console.print("\n[bold cyan]Step 2: Requirements Gathering[/bold cyan]\n")
            survey_data = self.run_user_survey(scan_data)
            
            # Get recommendations
            self.console.print("\n[bold cyan]Step 3: Service Recommendations[/bold cyan]\n")
            recommendations = self.get_service_recommendations(scan_data, survey_data)
            
            # Display and confirm
            if self.display_recommendations(recommendations):
                # Deploy
                self.console.print("\n[bold cyan]Step 4: Deployment[/bold cyan]\n")
                self.deploy_services(recommendations, scan_data)
            else:
                self.console.print("[yellow]Installation cancelled.[/yellow]")
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Installation interrupted by user.[/yellow]")
        except Exception as e:
            logger.error(f"Installation failed: {str(e)}")
            self.console.print(f"\n[bold red]Installation failed: {str(e)}[/bold red]")
            self.console.print("[yellow]Please check the logs for more details.[/yellow]")


def main():
    """Main entry point."""
    installer = HomelabInstaller()
    installer.run()


if __name__ == "__main__":
    main()

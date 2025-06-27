#!/usr/bin/env python3
"""
User Survey Module
Conducts an interactive survey to understand user requirements and preferences.
"""

import questionary
from questionary import Style
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel


class UserSurvey:
    """Conducts interactive user survey with flow-based questions."""
    
    def __init__(self):
        self.console = Console()
        self.custom_style = Style([
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
    
    def conduct_survey(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct the full user survey."""
        survey_results = {}
        
        # Primary use case
        survey_results['primary_use'] = self._ask_primary_use()
        
        # Based on primary use, ask specific questions
        if survey_results['primary_use'] == 'media_server':
            survey_results['media_details'] = self._ask_media_server_details()
        elif survey_results['primary_use'] == 'development':
            survey_results['dev_details'] = self._ask_development_details()
        elif survey_results['primary_use'] == 'home_automation':
            survey_results['automation_details'] = self._ask_automation_details()
        elif survey_results['primary_use'] == 'privacy_security':
            survey_results['privacy_details'] = self._ask_privacy_details()
        
        # Common questions for all use cases
        survey_results['users'] = self._ask_user_count()
        survey_results['storage_needs'] = self._ask_storage_needs()
        survey_results['external_access'] = self._ask_external_access()
        survey_results['security_level'] = self._ask_security_level()
        survey_results['backup_preference'] = self._ask_backup_preference()
        survey_results['monitoring'] = self._ask_monitoring_preference()
        
        # Home server connection
        survey_results['home_server'] = self._ask_home_server_details()
        
        # Budget and resources
        survey_results['resource_limits'] = self._ask_resource_limits(scan_data)
        
        return survey_results
    
    def _ask_primary_use(self) -> str:
        """Ask about primary use case."""
        return questionary.select(
            "What's the primary purpose of your homelab?",
            choices=[
                questionary.Choice("🎬 Media Server (Plex, Jellyfin, etc.)", value="media_server"),
                questionary.Choice("💻 Development Environment", value="development"),
                questionary.Choice("🏠 Home Automation Hub", value="home_automation"),
                questionary.Choice("🔒 Privacy & Security Services", value="privacy_security"),
                questionary.Choice("📁 File Storage & Sync", value="file_storage"),
                questionary.Choice("🌐 Web Hosting", value="web_hosting"),
                questionary.Choice("🔧 Mixed/General Purpose", value="general")
            ],
            style=self.custom_style
        ).ask()
    
    def _ask_media_server_details(self) -> Dict[str, Any]:
        """Ask specific questions for media server setup."""
        details = {}
        
        details['content_type'] = questionary.checkbox(
            "What type of media will you be serving?",
            choices=[
                "Movies",
                "TV Shows",
                "Music",
                "Photos",
                "Live TV/DVR"
            ],
            style=self.custom_style
        ).ask()
        
        details['transcoding'] = questionary.confirm(
            "Do you need hardware transcoding support?",
            default=True,
            style=self.custom_style
        ).ask()
        
        details['users_concurrent'] = questionary.select(
            "How many concurrent streams do you expect?",
            choices=["1-2", "3-5", "6-10", "More than 10"],
            style=self.custom_style
        ).ask()
        
        return details
    
    def _ask_development_details(self) -> Dict[str, Any]:
        """Ask specific questions for development environment."""
        details = {}
        
        details['languages'] = questionary.checkbox(
            "Which programming languages/frameworks will you use?",
            choices=[
                "Python",
                "JavaScript/Node.js",
                "Java",
                "Go",
                "Rust",
                "PHP",
                "Ruby",
                ".NET/C#",
                "Other"
            ],
            style=self.custom_style
        ).ask()
        
        details['tools'] = questionary.checkbox(
            "Which development tools do you need?",
            choices=[
                "Git repository (GitLab/Gitea)",
                "CI/CD Pipeline",
                "Container Registry",
                "Code Server (VS Code in browser)",
                "Database servers",
                "Message queues"
            ],
            style=self.custom_style
        ).ask()
        
        details['team_size'] = questionary.select(
            "How many developers will use this?",
            choices=["Just me", "2-5", "6-10", "More than 10"],
            style=self.custom_style
        ).ask()
        
        return details
    
    def _ask_automation_details(self) -> Dict[str, Any]:
        """Ask specific questions for home automation."""
        details = {}
        
        details['platform'] = questionary.select(
            "Which home automation platform do you prefer?",
            choices=[
                "Home Assistant",
                "OpenHAB",
                "Domoticz",
                "Node-RED only",
                "Not sure yet"
            ],
            style=self.custom_style
        ).ask()
        
        details['integrations'] = questionary.checkbox(
            "What types of devices will you integrate?",
            choices=[
                "Smart lights",
                "Thermostats",
                "Security cameras",
                "Door locks",
                "Sensors (motion, temperature, etc.)",
                "Voice assistants",
                "Smart appliances"
            ],
            style=self.custom_style
        ).ask()
        
        return details
    
    def _ask_privacy_details(self) -> Dict[str, Any]:
        """Ask specific questions for privacy/security setup."""
        details = {}
        
        details['services'] = questionary.checkbox(
            "Which privacy/security services do you need?",
            choices=[
                "VPN Server",
                "Ad Blocker (Pi-hole/AdGuard)",
                "Password Manager",
                "Encrypted File Storage",
                "Secure Communication",
                "Network Monitoring",
                "Firewall Management"
            ],
            style=self.custom_style
        ).ask()
        
        details['threat_model'] = questionary.select(
            "What's your primary security concern?",
            choices=[
                "Basic privacy from ISP/advertisers",
                "Protection from common threats",
                "Advanced security for sensitive data",
                "Maximum security and anonymity"
            ],
            style=self.custom_style
        ).ask()
        
        return details
    
    def _ask_user_count(self) -> str:
        """Ask about number of users."""
        return questionary.select(
            "How many users will access your homelab?",
            choices=["Just me", "2-5 (family)", "6-20 (small team)", "More than 20"],
            style=self.custom_style
        ).ask()
    
    def _ask_storage_needs(self) -> Dict[str, Any]:
        """Ask about storage requirements."""
        storage = {}
        
        storage['size'] = questionary.select(
            "How much data do you need to store?",
            choices=[
                "Less than 1TB",
                "1-5TB",
                "5-20TB",
                "20-50TB",
                "More than 50TB"
            ],
            style=self.custom_style
        ).ask()
        
        storage['growth'] = questionary.select(
            "How fast do you expect your storage needs to grow?",
            choices=[
                "Minimal growth",
                "Steady growth (20-50% per year)",
                "Rapid growth (doubling yearly)",
                "Exponential growth"
            ],
            style=self.custom_style
        ).ask()
        
        return storage
    
    def _ask_external_access(self) -> Dict[str, Any]:
        """Ask about external access requirements."""
        access = {}
        
        access['needed'] = questionary.confirm(
            "Do you need to access your homelab from outside your home network?",
            default=True,
            style=self.custom_style
        ).ask()
        
        if access['needed']:
            access['method'] = questionary.select(
                "How would you prefer to access it remotely?",
                choices=[
                    "VPN (most secure)",
                    "Reverse proxy with authentication",
                    "Cloudflare Tunnel",
                    "Direct port forwarding (least secure)",
                    "Not sure"
                ],
                style=self.custom_style
            ).ask()
            
            access['services'] = questionary.checkbox(
                "Which services need external access?",
                choices=[
                    "Web interfaces only",
                    "Media streaming",
                    "File access",
                    "Development tools",
                    "Everything"
                ],
                style=self.custom_style
            ).ask()
        
        return access
    
    def _ask_security_level(self) -> str:
        """Ask about desired security level."""
        return questionary.select(
            "What level of security do you need?",
            choices=[
                questionary.Choice("🟢 Basic - Standard security practices", value="basic"),
                questionary.Choice("🟡 Enhanced - Additional security layers", value="enhanced"),
                questionary.Choice("🟠 High - Strong security focus", value="high"),
                questionary.Choice("🔴 Maximum - Paranoid level security", value="maximum")
            ],
            style=self.custom_style
        ).ask()
    
    def _ask_backup_preference(self) -> Dict[str, Any]:
        """Ask about backup preferences."""
        backup = {}
        
        backup['strategy'] = questionary.select(
            "What's your backup strategy?",
            choices=[
                "Local backups only",
                "Cloud backups",
                "Both local and cloud",
                "No automated backups"
            ],
            style=self.custom_style
        ).ask()
        
        if backup['strategy'] != "No automated backups":
            backup['frequency'] = questionary.select(
                "How often should backups run?",
                choices=["Daily", "Weekly", "Monthly", "Real-time sync"],
                style=self.custom_style
            ).ask()
        
        return backup
    
    def _ask_monitoring_preference(self) -> Dict[str, Any]:
        """Ask about monitoring preferences."""
        monitoring = {}
        
        monitoring['level'] = questionary.select(
            "What level of monitoring do you want?",
            choices=[
                "Basic uptime monitoring",
                "Detailed metrics and logs",
                "Full observability stack",
                "No monitoring"
            ],
            style=self.custom_style
        ).ask()
        
        if monitoring['level'] != "No monitoring":
            monitoring['alerts'] = questionary.confirm(
                "Do you want to receive alerts for issues?",
                default=True,
                style=self.custom_style
            ).ask()
            
            if monitoring['alerts']:
                monitoring['alert_methods'] = questionary.checkbox(
                    "How should you be notified?",
                    choices=["Email", "SMS", "Push notifications", "Discord/Slack"],
                    style=self.custom_style
                ).ask()
        
        return monitoring
    
    def _ask_home_server_details(self) -> Dict[str, Any]:
        """Ask about home server connection details."""
        home_server = {}
        
        home_server['exists'] = questionary.confirm(
            "Do you have an existing home server to connect?",
            default=False,
            style=self.custom_style
        ).ask()
        
        if home_server['exists']:
            home_server['connection_type'] = questionary.select(
                "How is your home internet connection?",
                choices=[
                    "Static IP address",
                    "Dynamic IP with DDNS",
                    "Behind CGNAT",
                    "Not sure"
                ],
                style=self.custom_style
            ).ask()
            
            home_server['upload_speed'] = questionary.select(
                "What's your home upload speed?",
                choices=[
                    "Less than 10 Mbps",
                    "10-50 Mbps",
                    "50-100 Mbps",
                    "100-500 Mbps",
                    "1 Gbps or more"
                ],
                style=self.custom_style
            ).ask()
        
        return home_server
    
    def _ask_resource_limits(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ask about resource allocation preferences."""
        resources = {}
        
        # Show current resources
        env_data = scan_data.get('environment', {})
        self.console.print(Panel(
            f"[cyan]Detected Resources:[/cyan]\n"
            f"CPU Cores: {env_data.get('cpu_count', 'Unknown')}\n"
            f"RAM: {env_data.get('memory', {}).get('total_gb', 0):.1f} GB\n"
            f"Free Disk: {env_data.get('disk', {}).get('free_gb', 0):.1f} GB",
            title="System Resources",
            border_style="blue"
        ))
        
        resources['cpu_allocation'] = questionary.select(
            "How much CPU should the homelab use?",
            choices=[
                "Conservative (50% max)",
                "Balanced (75% max)",
                "Performance (90% max)",
                "All available"
            ],
            style=self.custom_style
        ).ask()
        
        resources['memory_allocation'] = questionary.select(
            "How much RAM should the homelab use?",
            choices=[
                "Conservative (50% max)",
                "Balanced (75% max)",
                "Performance (90% max)",
                "All available"
            ],
            style=self.custom_style
        ).ask()
        
        resources['growth_plan'] = questionary.confirm(
            "Do you plan to add more resources in the future?",
            default=False,
            style=self.custom_style
        ).ask()
        
        return resources
    
    def get_summary(self, survey_results: Dict[str, Any]) -> str:
        """Generate a summary of survey results."""
        summary = []
        summary.append(f"Primary Use: {survey_results.get('primary_use', 'Unknown')}")
        summary.append(f"Users: {survey_results.get('users', 'Unknown')}")
        summary.append(f"Security Level: {survey_results.get('security_level', 'Unknown')}")
        
        if survey_results.get('external_access', {}).get('needed'):
            summary.append(f"Remote Access: {survey_results['external_access'].get('method', 'Unknown')}")
        
        if survey_results.get('home_server', {}).get('exists'):
            summary.append("Home Server: Yes")
        
        return "\n".join(summary)


if __name__ == "__main__":
    # Test the survey
    survey = UserSurvey()
    results = survey.conduct_survey({'environment': {'cpu_count': 4, 'memory': {'total_gb': 8}, 'disk': {'free_gb': 100}}})
    print("\nSurvey Results:")
    print(survey.get_summary(results))

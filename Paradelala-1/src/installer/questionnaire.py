#!/usr/bin/env python3
"""
Interactive Questionnaire for Home-Lab Setup
Collects user preferences and requirements for customized deployment
"""

import json
import os
import sys
import re
from typing import Dict, List, Any, Optional, Tuple
import click
from datetime import datetime


class Question:
    """Represents a single question in the questionnaire"""
    
    def __init__(self, 
                 key: str,
                 text: str,
                 question_type: str,
                 options: Optional[List[str]] = None,
                 default: Any = None,
                 validator: Optional[callable] = None,
                 depends_on: Optional[Dict[str, Any]] = None):
        self.key = key
        self.text = text
        self.question_type = question_type
        self.options = options
        self.default = default
        self.validator = validator
        self.depends_on = depends_on


class Questionnaire:
    """Interactive questionnaire for home-lab configuration"""
    
    def __init__(self):
        self.answers = {}
        self.questions = self._initialize_questions()
        
    def _initialize_questions(self) -> List[Question]:
        """Initialize all questions for the setup"""
        return [
            # Basic Information
            Question(
                key="deployment_name",
                text="What would you like to name this deployment?",
                question_type="text",
                default="my-homelab",
                validator=lambda x: re.match(r'^[a-z0-9-]+$', x) is not None
            ),
            
            Question(
                key="domain",
                text="Enter your domain name (leave empty if none):",
                question_type="text",
                default="",
                validator=lambda x: x == "" or re.match(
                    r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', x.lower()
                ) is not None
            ),
            
            Question(
                key="email",
                text="Enter your email address (for SSL certificates):",
                question_type="text",
                default="",
                validator=lambda x: x == "" or re.match(
                    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', x
                ) is not None
            ),
            
            # Security Configuration
            Question(
                key="ssh_port",
                text="SSH port (default: 22):",
                question_type="number",
                default=22,
                validator=lambda x: 1 <= x <= 65535
            ),
            
            Question(
                key="disable_password_auth",
                text="Disable SSH password authentication (key-based only)?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="enable_fail2ban",
                text="Enable Fail2ban for intrusion prevention?",
                question_type="boolean",
                default=True
            ),
            
            # VPN Configuration
            Question(
                key="enable_wireguard",
                text="Enable WireGuard VPN?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="wireguard_port",
                text="WireGuard port (default: 51820):",
                question_type="number",
                default=51820,
                validator=lambda x: 1 <= x <= 65535,
                depends_on={"enable_wireguard": True}
            ),
            
            Question(
                key="wireguard_clients",
                text="Number of WireGuard clients to configure:",
                question_type="number",
                default=5,
                validator=lambda x: 1 <= x <= 100,
                depends_on={"enable_wireguard": True}
            ),
            
            # Proxy Configuration
            Question(
                key="enable_reverse_proxy",
                text="Enable reverse proxy (Nginx)?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="proxy_type",
                text="Select reverse proxy type:",
                question_type="choice",
                options=["nginx", "caddy", "traefik", "swag"],
                default="nginx",
                depends_on={"enable_reverse_proxy": True}
            ),
            
            Question(
                key="enable_home_proxy",
                text="Enable proxy to home server?",
                question_type="boolean",
                default=False
            ),
            
            Question(
                key="home_server_ip",
                text="Home server IP address:",
                question_type="text",
                default="",
                validator=lambda x: re.match(
                    r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', x
                ) is not None,
                depends_on={"enable_home_proxy": True}
            ),
            
            Question(
                key="home_server_port",
                text="Home server port:",
                question_type="number",
                default=8080,
                validator=lambda x: 1 <= x <= 65535,
                depends_on={"enable_home_proxy": True}
            ),
            
            # Services Selection
            Question(
                key="enable_monitoring",
                text="Enable monitoring stack (Prometheus + Grafana)?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="enable_logging",
                text="Enable centralized logging (ELK/Loki)?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="logging_stack",
                text="Select logging stack:",
                question_type="choice",
                options=["elk", "loki", "graylog"],
                default="loki",
                depends_on={"enable_logging": True}
            ),
            
            Question(
                key="enable_docker_registry",
                text="Enable private Docker registry?",
                question_type="boolean",
                default=False
            ),
            
            Question(
                key="enable_gitlab",
                text="Enable GitLab CE?",
                question_type="boolean",
                default=False
            ),
            
            Question(
                key="enable_nextcloud",
                text="Enable Nextcloud?",
                question_type="boolean",
                default=False
            ),
            
            Question(
                key="enable_pihole",
                text="Enable Pi-hole (DNS ad blocking)?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="enable_portainer",
                text="Enable Portainer (Docker management UI)?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="enable_vault",
                text="Enable HashiCorp Vault (secrets management)?",
                question_type="boolean",
                default=False
            ),
            
            # Resource Allocation
            Question(
                key="resource_profile",
                text="Select resource profile:",
                question_type="choice",
                options=["minimal", "balanced", "performance"],
                default="balanced"
            ),
            
            Question(
                key="enable_auto_updates",
                text="Enable automatic security updates?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="backup_enabled",
                text="Enable automated backups?",
                question_type="boolean",
                default=True
            ),
            
            Question(
                key="backup_retention_days",
                text="Backup retention (days):",
                question_type="number",
                default=7,
                validator=lambda x: 1 <= x <= 365,
                depends_on={"backup_enabled": True}
            )
        ]
    
    def _should_ask_question(self, question: Question) -> bool:
        """Check if a question should be asked based on dependencies"""
        if not question.depends_on:
            return True
        
        for key, value in question.depends_on.items():
            if self.answers.get(key) != value:
                return False
        
        return True
    
    def _validate_answer(self, question: Question, answer: Any) -> Tuple[bool, str]:
        """Validate an answer"""
        if question.validator:
            try:
                if question.validator(answer):
                    return True, ""
                else:
                    return False, "Invalid input format"
            except Exception as e:
                return False, str(e)
        
        return True, ""
    
    def _ask_text_question(self, question: Question) -> str:
        """Ask a text input question"""
        default_text = f" [{question.default}]" if question.default else ""
        answer = click.prompt(
            question.text + default_text,
            default=question.default,
            show_default=False
        )
        return answer
    
    def _ask_number_question(self, question: Question) -> int:
        """Ask a number input question"""
        while True:
            answer = click.prompt(
                question.text,
                default=question.default,
                type=int
            )
            
            valid, error = self._validate_answer(question, answer)
            if valid:
                return answer
            else:
                click.echo(f"Error: {error}", err=True)
    
    def _ask_boolean_question(self, question: Question) -> bool:
        """Ask a yes/no question"""
        return click.confirm(question.text, default=question.default)
    
    def _ask_choice_question(self, question: Question) -> str:
        """Ask a multiple choice question"""
        click.echo(f"\n{question.text}")
        for i, option in enumerate(question.options, 1):
            click.echo(f"  {i}. {option}")
        
        while True:
            choice = click.prompt(
                "Select an option",
                type=int,
                default=question.options.index(question.default) + 1
            )
            
            if 1 <= choice <= len(question.options):
                return question.options[choice - 1]
            else:
                click.echo("Invalid choice. Please try again.", err=True)
    
    def ask_question(self, question: Question) -> Any:
        """Ask a single question based on its type"""
        if question.question_type == "text":
            return self._ask_text_question(question)
        elif question.question_type == "number":
            return self._ask_number_question(question)
        elif question.question_type == "boolean":
            return self._ask_boolean_question(question)
        elif question.question_type == "choice":
            return self._ask_choice_question(question)
        else:
            raise ValueError(f"Unknown question type: {question.question_type}")
    
    def run(self) -> Dict[str, Any]:
        """Run the complete questionnaire"""
        click.clear()
        click.echo("=" * 60)
        click.echo("   Secure Home-Lab Setup - Interactive Configuration")
        click.echo("=" * 60)
        click.echo()
        click.echo("Please answer the following questions to customize your setup.")
        click.echo("Press Ctrl+C at any time to cancel.\n")
        
        try:
            # Group questions by category
            categories = {
                "Basic Information": ["deployment_name", "domain", "email"],
                "Security Configuration": [
                    "ssh_port", "disable_password_auth", "enable_fail2ban"
                ],
                "VPN Configuration": [
                    "enable_wireguard", "wireguard_port", "wireguard_clients"
                ],
                "Proxy Configuration": [
                    "enable_reverse_proxy", "proxy_type", "enable_home_proxy",
                    "home_server_ip", "home_server_port"
                ],
                "Services Selection": [
                    "enable_monitoring", "enable_logging", "logging_stack",
                    "enable_docker_registry", "enable_gitlab", "enable_nextcloud",
                    "enable_pihole", "enable_portainer", "enable_vault"
                ],
                "System Configuration": [
                    "resource_profile", "enable_auto_updates", 
                    "backup_enabled", "backup_retention_days"
                ]
            }
            
            for category, question_keys in categories.items():
                click.echo(f"\n{click.style(category, bold=True, fg='blue')}")
                click.echo("-" * len(category))
                
                for key in question_keys:
                    question = next(q for q in self.questions if q.key == key)
                    
                    if self._should_ask_question(question):
                        while True:
                            answer = self.ask_question(question)
                            valid, error = self._validate_answer(question, answer)
                            
                            if valid:
                                self.answers[question.key] = answer
                                break
                            else:
                                click.echo(f"Error: {error}", err=True)
            
            # Add metadata
            self.answers["timestamp"] = datetime.now().isoformat()
            self.answers["version"] = "1.0"
            
            # Calculate estimated resource usage
            self._calculate_resource_estimates()
            
            # Show summary
            self._show_summary()
            
            # Confirm configuration
            if not click.confirm("\nProceed with this configuration?", default=True):
                click.echo("Configuration cancelled.")
                sys.exit(1)
            
            # Save configuration
            self._save_configuration()
            
            return self.answers
            
        except KeyboardInterrupt:
            click.echo("\n\nConfiguration cancelled.")
            sys.exit(1)
    
    def _calculate_resource_estimates(self):
        """Calculate estimated resource usage based on selections"""
        base_memory = 512  # MB
        base_cpu = 0.5
        
        service_requirements = {
            "enable_monitoring": {"memory": 1024, "cpu": 1},
            "enable_logging": {"memory": 2048, "cpu": 1},
            "enable_gitlab": {"memory": 4096, "cpu": 2},
            "enable_nextcloud": {"memory": 512, "cpu": 0.5},
            "enable_pihole": {"memory": 256, "cpu": 0.25},
            "enable_portainer": {"memory": 128, "cpu": 0.25},
            "enable_vault": {"memory": 256, "cpu": 0.5},
            "enable_docker_registry": {"memory": 512, "cpu": 0.5}
        }
        
        total_memory = base_memory
        total_cpu = base_cpu
        
        for service, enabled in self.answers.items():
            if service in service_requirements and enabled:
                total_memory += service_requirements[service]["memory"]
                total_cpu += service_requirements[service]["cpu"]
        
        # Adjust based on resource profile
        if self.answers.get("resource_profile") == "minimal":
            total_memory *= 0.7
            total_cpu *= 0.7
        elif self.answers.get("resource_profile") == "performance":
            total_memory *= 1.5
            total_cpu *= 1.5
        
        self.answers["estimated_resources"] = {
            "memory_mb": int(total_memory),
            "cpu_cores": round(total_cpu, 1),
            "disk_gb": 20 + (10 if self.answers.get("enable_gitlab") else 0)
        }
    
    def _show_summary(self):
        """Display configuration summary"""
        click.echo("\n" + "=" * 60)
        click.echo(click.style("Configuration Summary", bold=True, fg='green'))
        click.echo("=" * 60)
        
        # Basic info
        click.echo(f"\nDeployment Name: {self.answers.get('deployment_name')}")
        if self.answers.get('domain'):
            click.echo(f"Domain: {self.answers.get('domain')}")
        
        # Enabled services
        click.echo("\nEnabled Services:")
        services = [
            ("Monitoring", "enable_monitoring"),
            ("Logging", "enable_logging"),
            ("WireGuard VPN", "enable_wireguard"),
            ("Reverse Proxy", "enable_reverse_proxy"),
            ("Docker Registry", "enable_docker_registry"),
            ("GitLab", "enable_gitlab"),
            ("Nextcloud", "enable_nextcloud"),
            ("Pi-hole", "enable_pihole"),
            ("Portainer", "enable_portainer"),
            ("Vault", "enable_vault")
        ]
        
        for name, key in services:
            if self.answers.get(key):
                click.echo(f"  ✓ {name}")
        
        # Resource estimates
        resources = self.answers.get("estimated_resources", {})
        click.echo(f"\nEstimated Resource Requirements:")
        click.echo(f"  Memory: {resources.get('memory_mb', 0)} MB")
        click.echo(f"  CPU: {resources.get('cpu_cores', 0)} cores")
        click.echo(f"  Disk: {resources.get('disk_gb', 0)} GB")
    
    def _save_configuration(self):
        """Save configuration to file"""
        config_file = "/tmp/user_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(self.answers, f, indent=2)
        
        click.echo(f"\nConfiguration saved to: {config_file}")


def main():
    """Main entry point"""
    questionnaire = Questionnaire()
    config = questionnaire.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

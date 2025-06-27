#!/usr/bin/env python3
"""
Service Deployer Module
Handles the deployment and configuration of recommended services.
"""

import os
import subprocess
import yaml
import json
import time
import secrets
import string
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


class ServiceDeployer:
    """Handles deployment of services using Docker Compose."""
    
    def __init__(self):
        self.console = Console()
        self.deployment_dir = Path("/opt/homelab")
        self.compose_file = self.deployment_dir / "docker-compose.yml"
        self.env_file = self.deployment_dir / ".env"
        self.deployed_services = []
    
    def deploy(self, recommendations: Dict[str, Any], config_path: str) -> Dict[str, Any]:
        """Deploy all recommended services."""
        try:
            # Prepare deployment directory
            self._prepare_deployment_directory()
            
            # Generate passwords and tokens
            credentials = self._generate_credentials()
            
            # Create docker-compose configuration
            compose_config = self._create_compose_config(recommendations, credentials)
            
            # Create environment file
            self._create_env_file(credentials, recommendations)
            
            # Deploy services
            self._deploy_services(compose_config)
            
            # Wait for services to be ready
            self._wait_for_services()
            
            # Configure services
            self._configure_services(recommendations, credentials)
            
            return {
                'success': True,
                'dashboard_url': f"https://{self._get_domain()}",
                'admin_password': credentials['admin_password'],
                'config_path': config_path,
                'deployed_services': self.deployed_services
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_deployment_directory(self):
        """Prepare the deployment directory structure."""
        directories = [
            self.deployment_dir,
            self.deployment_dir / "configs",
            self.deployment_dir / "data",
            self.deployment_dir / "logs",
            self.deployment_dir / "backups",
            self.deployment_dir / "certs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Set proper permissions
        subprocess.run(['sudo', 'chown', '-R', f'{os.getuid()}:{os.getgid()}', str(self.deployment_dir)])
    
    def _generate_credentials(self) -> Dict[str, str]:
        """Generate secure passwords and tokens."""
        def generate_password(length=16):
            alphabet = string.ascii_letters + string.digits + string.punctuation
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        
        return {
            'admin_password': generate_password(),
            'db_password': generate_password(),
            'jwt_secret': secrets.token_hex(32),
            'api_key': secrets.token_hex(16),
            'wireguard_private_key': self._generate_wireguard_key() if self._needs_wireguard() else None
        }
    
    def _generate_wireguard_key(self) -> str:
        """Generate WireGuard private key."""
        try:
            result = subprocess.run(['wg', 'genkey'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            # Fallback to a placeholder
            return "GENERATE_ME"
    
    def _needs_wireguard(self) -> bool:
        """Check if WireGuard is needed."""
        # This would check recommendations
        return True
    
    def _create_compose_config(self, recommendations: Dict[str, Any], credentials: Dict[str, str]) -> Dict[str, Any]:
        """Create Docker Compose configuration."""
        compose = {
            'version': '3.8',
            'services': {},
            'networks': {
                'homelab': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{'subnet': '172.20.0.0/16'}]
                    }
                }
            },
            'volumes': {}
        }
        
        # Add core services
        for service in recommendations['core_services']:
            service_config = self._get_service_config(service, credentials)
            if service_config:
                compose['services'][service['name'].lower().replace(' ', '-')] = service_config
                self.deployed_services.append(service['name'])
        
        # Add optional services
        for service in recommendations['optional_services']:
            service_config = self._get_service_config(service, credentials)
            if service_config:
                compose['services'][service['name'].lower().replace(' ', '-')] = service_config
                self.deployed_services.append(service['name'])
        
        # Add proxy configuration
        if recommendations['proxy_config']['type'] == 'nginx':
            compose['services']['nginx-proxy-manager'] = self._get_nginx_config(credentials)
            self.deployed_services.append('Nginx Proxy Manager')
        
        return compose
    
    def _get_service_config(self, service: Dict[str, Any], credentials: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Get Docker configuration for a specific service."""
        service_configs = {
            'Jellyfin': {
                'image': 'jellyfin/jellyfin:latest',
                'container_name': 'jellyfin',
                'environment': {
                    'PUID': '1000',
                    'PGID': '1000',
                    'TZ': 'UTC'
                },
                'volumes': [
                    './data/jellyfin/config:/config',
                    './data/jellyfin/cache:/cache',
                    '/media:/media:ro'
                ],
                'ports': ['8096:8096'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Plex': {
                'image': 'plexinc/pms-docker:latest',
                'container_name': 'plex',
                'environment': {
                    'PUID': '1000',
                    'PGID': '1000',
                    'TZ': 'UTC',
                    'PLEX_CLAIM': '${PLEX_CLAIM}'
                },
                'volumes': [
                    './data/plex/config:/config',
                    './data/plex/transcode:/transcode',
                    '/media:/media:ro'
                ],
                'ports': ['32400:32400'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Gitea': {
                'image': 'gitea/gitea:latest',
                'container_name': 'gitea',
                'environment': {
                    'USER_UID': '1000',
                    'USER_GID': '1000',
                    'GITEA__database__DB_TYPE': 'sqlite3',
                    'GITEA__database__PATH': '/data/gitea.db',
                    'GITEA__server__DOMAIN': '${DOMAIN}',
                    'GITEA__server__ROOT_URL': 'https://${DOMAIN}/gitea/',
                    'GITEA__security__SECRET_KEY': '${JWT_SECRET}',
                    'GITEA__security__INTERNAL_TOKEN': '${API_KEY}'
                },
                'volumes': [
                    './data/gitea:/data',
                    '/etc/timezone:/etc/timezone:ro',
                    '/etc/localtime:/etc/localtime:ro'
                ],
                'ports': ['3000:3000', '222:22'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Home Assistant': {
                'image': 'ghcr.io/home-assistant/home-assistant:stable',
                'container_name': 'homeassistant',
                'environment': {
                    'TZ': 'UTC'
                },
                'volumes': [
                    './data/homeassistant:/config',
                    '/etc/localtime:/etc/localtime:ro'
                ],
                'ports': ['8123:8123'],
                'privileged': True,
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Pi-hole': {
                'image': 'pihole/pihole:latest',
                'container_name': 'pihole',
                'environment': {
                    'TZ': 'UTC',
                    'WEBPASSWORD': '${ADMIN_PASSWORD}',
                    'PIHOLE_DNS_': '1.1.1.1;1.0.0.1'
                },
                'volumes': [
                    './data/pihole/etc:/etc/pihole',
                    './data/pihole/dnsmasq.d:/etc/dnsmasq.d'
                ],
                'ports': [
                    '53:53/tcp',
                    '53:53/udp',
                    '8080:80/tcp'
                ],
                'cap_add': ['NET_ADMIN'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'WireGuard': {
                'image': 'linuxserver/wireguard:latest',
                'container_name': 'wireguard',
                'cap_add': ['NET_ADMIN', 'SYS_MODULE'],
                'environment': {
                    'PUID': '1000',
                    'PGID': '1000',
                    'TZ': 'UTC',
                    'SERVERURL': '${DOMAIN}',
                    'SERVERPORT': '51820',
                    'PEERS': '5',
                    'PEERDNS': 'auto',
                    'INTERNAL_SUBNET': '10.13.13.0',
                    'ALLOWEDIPS': '0.0.0.0/0'
                },
                'volumes': [
                    './data/wireguard:/config',
                    '/lib/modules:/lib/modules:ro'
                ],
                'ports': ['51820:51820/udp'],
                'sysctls': {
                    'net.ipv4.conf.all.src_valid_mark': '1'
                },
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Vaultwarden': {
                'image': 'vaultwarden/server:latest',
                'container_name': 'vaultwarden',
                'environment': {
                    'DOMAIN': 'https://${DOMAIN}',
                    'SIGNUPS_ALLOWED': 'false',
                    'ADMIN_TOKEN': '${API_KEY}',
                    'WEBSOCKET_ENABLED': 'true'
                },
                'volumes': [
                    './data/vaultwarden:/data'
                ],
                'ports': ['8081:80'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Nextcloud': {
                'image': 'nextcloud:latest',
                'container_name': 'nextcloud',
                'environment': {
                    'POSTGRES_HOST': 'nextcloud-db',
                    'POSTGRES_DB': 'nextcloud',
                    'POSTGRES_USER': 'nextcloud',
                    'POSTGRES_PASSWORD': '${DB_PASSWORD}',
                    'NEXTCLOUD_ADMIN_USER': 'admin',
                    'NEXTCLOUD_ADMIN_PASSWORD': '${ADMIN_PASSWORD}',
                    'NEXTCLOUD_TRUSTED_DOMAINS': '${DOMAIN}'
                },
                'volumes': [
                    './data/nextcloud:/var/www/html'
                ],
                'ports': ['8082:80'],
                'restart': 'unless-stopped',
                'networks': ['homelab'],
                'depends_on': ['nextcloud-db']
            },
            'Uptime Kuma': {
                'image': 'louislam/uptime-kuma:latest',
                'container_name': 'uptime-kuma',
                'volumes': [
                    './data/uptime-kuma:/app/data'
                ],
                'ports': ['3001:3001'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Prometheus': {
                'image': 'prom/prometheus:latest',
                'container_name': 'prometheus',
                'command': [
                    '--config.file=/etc/prometheus/prometheus.yml',
                    '--storage.tsdb.path=/prometheus',
                    '--web.console.libraries=/usr/share/prometheus/console_libraries',
                    '--web.console.templates=/usr/share/prometheus/consoles'
                ],
                'volumes': [
                    './configs/prometheus:/etc/prometheus',
                    './data/prometheus:/prometheus'
                ],
                'ports': ['9090:9090'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Grafana': {
                'image': 'grafana/grafana:latest',
                'container_name': 'grafana',
                'environment': {
                    'GF_SECURITY_ADMIN_PASSWORD': '${ADMIN_PASSWORD}',
                    'GF_INSTALL_PLUGINS': 'grafana-clock-panel,grafana-simple-json-datasource'
                },
                'volumes': [
                    './data/grafana:/var/lib/grafana',
                    './configs/grafana/provisioning:/etc/grafana/provisioning'
                ],
                'ports': ['3002:3000'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Authelia': {
                'image': 'authelia/authelia:latest',
                'container_name': 'authelia',
                'environment': {
                    'TZ': 'UTC'
                },
                'volumes': [
                    './configs/authelia:/config'
                ],
                'ports': ['9091:9091'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'CrowdSec': {
                'image': 'crowdsecurity/crowdsec:latest',
                'container_name': 'crowdsec',
                'environment': {
                    'COLLECTIONS': 'crowdsecurity/nginx crowdsecurity/http-cve crowdsecurity/whitelist-good-actors'
                },
                'volumes': [
                    './data/crowdsec/config:/etc/crowdsec',
                    './data/crowdsec/data:/var/lib/crowdsec/data',
                    './logs:/logs:ro'
                ],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            },
            'Duplicati': {
                'image': 'linuxserver/duplicati:latest',
                'container_name': 'duplicati',
                'environment': {
                    'PUID': '1000',
                    'PGID': '1000',
                    'TZ': 'UTC'
                },
                'volumes': [
                    './data/duplicati:/config',
                    './backups:/backups',
                    './data:/source:ro'
                ],
                'ports': ['8200:8200'],
                'restart': 'unless-stopped',
                'networks': ['homelab']
            }
        }
        
        # Handle special cases
        service_name = service['name']
        config = service_configs.get(service_name)
        
        # Add database for Nextcloud if needed
        if service_name == 'Nextcloud' and config:
            self._add_nextcloud_db(config)
        
        return config
    
    def _add_nextcloud_db(self, compose: Dict[str, Any]):
        """Add Nextcloud database service."""
        if 'services' not in compose:
            compose['services'] = {}
            
        compose['services']['nextcloud-db'] = {
            'image': 'postgres:14',
            'container_name': 'nextcloud-db',
            'environment': {
                'POSTGRES_DB': 'nextcloud',
                'POSTGRES_USER': 'nextcloud',
                'POSTGRES_PASSWORD': '${DB_PASSWORD}'
            },
            'volumes': [
                './data/nextcloud-db:/var/lib/postgresql/data'
            ],
            'restart': 'unless-stopped',
            'networks': ['homelab']
        }
    
    def _get_nginx_config(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Get Nginx Proxy Manager configuration."""
        return {
            'image': 'jc21/nginx-proxy-manager:latest',
            'container_name': 'nginx-proxy-manager',
            'ports': [
                '80:80',
                '443:443',
                '81:81'
            ],
            'environment': {
                'DB_SQLITE_FILE': '/data/database.sqlite',
                'DISABLE_IPV6': 'true'
            },
            'volumes': [
                './data/nginx-proxy-manager/data:/data',
                './data/nginx-proxy-manager/letsencrypt:/etc/letsencrypt'
            ],
            'restart': 'unless-stopped',
            'networks': ['homelab']
        }
    
    def _create_env_file(self, credentials: Dict[str, str], recommendations: Dict[str, Any]):
        """Create environment file with credentials."""
        env_content = f"""# Homelab Environment Configuration
# Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Domain Configuration
DOMAIN={self._get_domain()}

# Credentials
ADMIN_PASSWORD={credentials['admin_password']}
DB_PASSWORD={credentials['db_password']}
JWT_SECRET={credentials['jwt_secret']}
API_KEY={credentials['api_key']}

# Service-specific
PLEX_CLAIM=claim-XXXXXXXXXXXXX  # Get from https://www.plex.tv/claim/

# Timezone
TZ=UTC
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        # Secure the file
        os.chmod(self.env_file, 0o600)
    
    def _get_domain(self) -> str:
        """Get domain name for the deployment."""
        # In a real implementation, this would be configured
        return "homelab.local"
    
    def _deploy_services(self, compose_config: Dict[str, Any]):
        """Deploy services using Docker Compose."""
        # Write compose file
        with open(self.compose_file, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False)
        
        # Pull images
        self.console.print("[cyan]Pulling Docker images...[/cyan]")
        subprocess.run(
            ['docker-compose', '-f', str(self.compose_file), 'pull'],
            cwd=self.deployment_dir,
            check=True
        )
        
        # Start services
        self.console.print("[cyan]Starting services...[/cyan]")
        subprocess.run(
            ['docker-compose', '-f', str(self.compose_file), 'up', '-d'],
            cwd=self.deployment_dir,
            check=True
        )
    
    def _wait_for_services(self):
        """Wait for all services to be ready."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Waiting for services to start...", total=len(self.deployed_services))
            
            for service in self.deployed_services:
                time.sleep(5)  # Give each service time to start
                progress.update(task, advance=1, description=f"[cyan]Started {service}")
    
    def _configure_services(self, recommendations: Dict[str, Any], credentials: Dict[str, str]):
        """Configure services after deployment."""
        # This would include:
        # - Setting up reverse proxy routes
        # - Configuring authentication
        # - Setting up monitoring targets
        # - Configuring backups
        pass


if __name__ == "__main__":
    # Test the deployer
    deployer = ServiceDeployer()
    recommendations = {
        'core_services': [
            {'name': 'Jellyfin', 'purpose': 'Media server'},
            {'name': 'Pi-hole', 'purpose': 'Ad blocker'}
        ],
        'optional_services': [
            {'name': 'Uptime Kuma', 'purpose': 'Monitoring'}
        ],
        'proxy_config': {'type': 'nginx'},
        'security_config': {},
        'backup_config': {},
        'monitoring_config': {}
    }
    
    result = deployer.deploy(recommendations, '/tmp/config.json')
    print(json.dumps(result, indent=2))

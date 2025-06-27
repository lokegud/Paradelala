#!/usr/bin/env python3
"""
Service Recommender Agent
AI-powered agent that recommends services based on user requirements and system capabilities.
"""

from typing import Dict, Any, List
import json


class ServiceRecommender:
    """Agent that recommends services based on analysis and survey results."""
    
    def __init__(self):
        self.service_catalog = self._load_service_catalog()
    
    def _load_service_catalog(self) -> Dict[str, Any]:
        """Load the service catalog with all available services."""
        return {
            # Media Services
            'jellyfin': {
                'name': 'Jellyfin',
                'category': 'media',
                'purpose': 'Open-source media server',
                'resources': {'cpu': '2 cores', 'memory': '2GB', 'disk': '1GB'},
                'features': ['transcoding', 'multi-user', 'mobile-apps'],
                'difficulty': 'easy'
            },
            'plex': {
                'name': 'Plex',
                'category': 'media',
                'purpose': 'Popular media server with great apps',
                'resources': {'cpu': '2 cores', 'memory': '2GB', 'disk': '1GB'},
                'features': ['transcoding', 'multi-user', 'mobile-apps', 'plex-pass'],
                'difficulty': 'easy'
            },
            
            # Development Tools
            'gitlab': {
                'name': 'GitLab',
                'category': 'development',
                'purpose': 'Complete DevOps platform',
                'resources': {'cpu': '4 cores', 'memory': '4GB', 'disk': '10GB'},
                'features': ['git', 'ci-cd', 'container-registry', 'issue-tracking'],
                'difficulty': 'medium'
            },
            'gitea': {
                'name': 'Gitea',
                'category': 'development',
                'purpose': 'Lightweight Git service',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '1GB'},
                'features': ['git', 'issue-tracking', 'lightweight'],
                'difficulty': 'easy'
            },
            'code-server': {
                'name': 'Code Server',
                'category': 'development',
                'purpose': 'VS Code in the browser',
                'resources': {'cpu': '2 cores', 'memory': '2GB', 'disk': '1GB'},
                'features': ['ide', 'extensions', 'remote-development'],
                'difficulty': 'easy'
            },
            
            # Home Automation
            'home-assistant': {
                'name': 'Home Assistant',
                'category': 'automation',
                'purpose': 'Open-source home automation platform',
                'resources': {'cpu': '2 cores', 'memory': '2GB', 'disk': '5GB'},
                'features': ['integrations', 'automations', 'dashboards'],
                'difficulty': 'medium'
            },
            
            # Privacy & Security
            'pihole': {
                'name': 'Pi-hole',
                'category': 'privacy',
                'purpose': 'Network-wide ad blocker',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '1GB'},
                'features': ['ad-blocking', 'dns-server', 'statistics'],
                'difficulty': 'easy'
            },
            'adguard': {
                'name': 'AdGuard Home',
                'category': 'privacy',
                'purpose': 'Network-wide ad and tracker blocker',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '1GB'},
                'features': ['ad-blocking', 'dns-server', 'parental-control'],
                'difficulty': 'easy'
            },
            'wireguard': {
                'name': 'WireGuard',
                'category': 'privacy',
                'purpose': 'Modern VPN server',
                'resources': {'cpu': '1 core', 'memory': '256MB', 'disk': '100MB'},
                'features': ['vpn', 'fast', 'secure'],
                'difficulty': 'medium'
            },
            'vaultwarden': {
                'name': 'Vaultwarden',
                'category': 'privacy',
                'purpose': 'Bitwarden-compatible password manager',
                'resources': {'cpu': '1 core', 'memory': '256MB', 'disk': '1GB'},
                'features': ['password-manager', 'encryption', 'multi-device'],
                'difficulty': 'easy'
            },
            
            # File Storage
            'nextcloud': {
                'name': 'Nextcloud',
                'category': 'storage',
                'purpose': 'Self-hosted cloud storage',
                'resources': {'cpu': '2 cores', 'memory': '2GB', 'disk': '2GB'},
                'features': ['file-sync', 'collaboration', 'apps'],
                'difficulty': 'medium'
            },
            'syncthing': {
                'name': 'Syncthing',
                'category': 'storage',
                'purpose': 'Continuous file synchronization',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '100MB'},
                'features': ['p2p-sync', 'encryption', 'cross-platform'],
                'difficulty': 'easy'
            },
            
            # Monitoring
            'uptime-kuma': {
                'name': 'Uptime Kuma',
                'category': 'monitoring',
                'purpose': 'Modern uptime monitoring',
                'resources': {'cpu': '1 core', 'memory': '256MB', 'disk': '500MB'},
                'features': ['uptime-monitoring', 'notifications', 'status-pages'],
                'difficulty': 'easy'
            },
            'prometheus': {
                'name': 'Prometheus',
                'category': 'monitoring',
                'purpose': 'Metrics collection and alerting',
                'resources': {'cpu': '1 core', 'memory': '1GB', 'disk': '5GB'},
                'features': ['metrics', 'alerting', 'time-series'],
                'difficulty': 'hard'
            },
            'grafana': {
                'name': 'Grafana',
                'category': 'monitoring',
                'purpose': 'Metrics visualization',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '1GB'},
                'features': ['dashboards', 'visualization', 'alerts'],
                'difficulty': 'medium'
            },
            
            # Security
            'authelia': {
                'name': 'Authelia',
                'category': 'security',
                'purpose': 'Authentication and authorization server',
                'resources': {'cpu': '1 core', 'memory': '256MB', 'disk': '100MB'},
                'features': ['2fa', 'sso', 'ldap'],
                'difficulty': 'hard'
            },
            'crowdsec': {
                'name': 'CrowdSec',
                'category': 'security',
                'purpose': 'Collaborative security engine',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '500MB'},
                'features': ['ids', 'community-blocklists', 'api'],
                'difficulty': 'medium'
            },
            
            # Proxy/Reverse Proxy
            'nginx-proxy-manager': {
                'name': 'Nginx Proxy Manager',
                'category': 'proxy',
                'purpose': 'Easy reverse proxy with GUI',
                'resources': {'cpu': '1 core', 'memory': '256MB', 'disk': '500MB'},
                'features': ['reverse-proxy', 'ssl', 'gui'],
                'difficulty': 'easy'
            },
            'traefik': {
                'name': 'Traefik',
                'category': 'proxy',
                'purpose': 'Modern reverse proxy with auto-discovery',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '100MB'},
                'features': ['reverse-proxy', 'ssl', 'auto-discovery'],
                'difficulty': 'medium'
            },
            
            # Backup
            'duplicati': {
                'name': 'Duplicati',
                'category': 'backup',
                'purpose': 'Backup software with encryption',
                'resources': {'cpu': '1 core', 'memory': '512MB', 'disk': '1GB'},
                'features': ['encryption', 'cloud-support', 'scheduling'],
                'difficulty': 'easy'
            },
            'restic': {
                'name': 'Restic',
                'category': 'backup',
                'purpose': 'Fast, secure backup program',
                'resources': {'cpu': '1 core', 'memory': '256MB', 'disk': '100MB'},
                'features': ['encryption', 'deduplication', 'snapshots'],
                'difficulty': 'medium'
            }
        }
    
    def recommend(self, scan_data: Dict[str, Any], survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service recommendations based on scan and survey data."""
        recommendations = {
            'core_services': [],
            'optional_services': [],
            'proxy_config': {},
            'security_config': {},
            'backup_config': {},
            'monitoring_config': {}
        }
        
        # Analyze available resources
        resources = self._analyze_resources(scan_data)
        
        # Get core services based on primary use
        primary_use = survey_data.get('primary_use', 'general')
        recommendations['core_services'] = self._get_core_services(primary_use, survey_data, resources)
        
        # Get optional services
        recommendations['optional_services'] = self._get_optional_services(survey_data, resources)
        
        # Configure proxy/tunnel
        recommendations['proxy_config'] = self._configure_proxy(survey_data)
        
        # Configure security
        recommendations['security_config'] = self._configure_security(survey_data)
        
        # Configure backup
        recommendations['backup_config'] = self._configure_backup(survey_data)
        
        # Configure monitoring
        recommendations['monitoring_config'] = self._configure_monitoring(survey_data)
        
        return recommendations
    
    def _analyze_resources(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze available system resources."""
        env_data = scan_data.get('environment', {})
        
        return {
            'cpu_cores': env_data.get('cpu_count', 1),
            'memory_gb': env_data.get('memory', {}).get('available_gb', 1),
            'disk_gb': env_data.get('disk', {}).get('free_gb', 10),
            'docker_available': env_data.get('docker', {}).get('installed', False)
        }
    
    def _get_core_services(self, primary_use: str, survey_data: Dict[str, Any], resources: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get core services based on primary use case."""
        core_services = []
        
        # Always include a reverse proxy
        if resources['memory_gb'] > 4:
            core_services.append(self.service_catalog['traefik'])
        else:
            core_services.append(self.service_catalog['nginx-proxy-manager'])
        
        # Add services based on primary use
        if primary_use == 'media_server':
            media_details = survey_data.get('media_details', {})
            if 'plex-pass' in str(media_details):
                core_services.append(self.service_catalog['plex'])
            else:
                core_services.append(self.service_catalog['jellyfin'])
        
        elif primary_use == 'development':
            dev_details = survey_data.get('dev_details', {})
            if resources['memory_gb'] > 6:
                core_services.append(self.service_catalog['gitlab'])
            else:
                core_services.append(self.service_catalog['gitea'])
            
            if 'Code Server' in dev_details.get('tools', []):
                core_services.append(self.service_catalog['code-server'])
        
        elif primary_use == 'home_automation':
            core_services.append(self.service_catalog['home-assistant'])
        
        elif primary_use == 'privacy_security':
            privacy_details = survey_data.get('privacy_details', {})
            if 'Ad Blocker' in privacy_details.get('services', []):
                core_services.append(self.service_catalog['pihole'])
            if 'VPN Server' in privacy_details.get('services', []):
                core_services.append(self.service_catalog['wireguard'])
            if 'Password Manager' in privacy_details.get('services', []):
                core_services.append(self.service_catalog['vaultwarden'])
        
        elif primary_use == 'file_storage':
            if resources['memory_gb'] > 3:
                core_services.append(self.service_catalog['nextcloud'])
            else:
                core_services.append(self.service_catalog['syncthing'])
        
        return core_services
    
    def _get_optional_services(self, survey_data: Dict[str, Any], resources: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get optional services based on user preferences."""
        optional_services = []
        
        # Add monitoring based on preference
        monitoring = survey_data.get('monitoring', {})
        if monitoring.get('level') == 'Basic uptime monitoring':
            optional_services.append(self.service_catalog['uptime-kuma'])
        elif monitoring.get('level') in ['Detailed metrics and logs', 'Full observability stack']:
            if resources['memory_gb'] > 4:
                optional_services.append(self.service_catalog['prometheus'])
                optional_services.append(self.service_catalog['grafana'])
            else:
                optional_services.append(self.service_catalog['uptime-kuma'])
        
        # Add security services based on security level
        security_level = survey_data.get('security_level', 'basic')
        if security_level in ['high', 'maximum']:
            optional_services.append(self.service_catalog['crowdsec'])
            if resources['memory_gb'] > 4:
                optional_services.append(self.service_catalog['authelia'])
        
        # Add backup service if needed
        backup = survey_data.get('backup_preference', {})
        if backup.get('strategy') != 'No automated backups':
            if resources['memory_gb'] > 2:
                optional_services.append(self.service_catalog['duplicati'])
        
        return optional_services
    
    def _configure_proxy(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure proxy/tunnel settings."""
        external_access = survey_data.get('external_access', {})
        home_server = survey_data.get('home_server', {})
        
        config = {
            'type': 'nginx',
            'ssl_provider': 'letsencrypt',
            'tunnel_type': None
        }
        
        if external_access.get('needed'):
            method = external_access.get('method', 'VPN')
            if method == 'VPN (most secure)':
                config['tunnel_type'] = 'wireguard'
            elif method == 'Cloudflare Tunnel':
                config['tunnel_type'] = 'cloudflare'
            elif method == 'Reverse proxy with authentication':
                config['tunnel_type'] = 'reverse_proxy'
                config['auth_required'] = True
        
        if home_server.get('exists'):
            if home_server.get('connection_type') == 'Behind CGNAT':
                config['tunnel_type'] = 'cloudflare'  # Best for CGNAT
        
        return config
    
    def _configure_security(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure security settings."""
        security_level = survey_data.get('security_level', 'basic')
        
        config = {
            'firewall': 'ufw',
            'fail2ban': False,
            'auth_method': 'basic',
            'ssl_strict': False
        }
        
        if security_level == 'enhanced':
            config['fail2ban'] = True
            config['auth_method'] = 'oauth2'
        elif security_level == 'high':
            config['fail2ban'] = True
            config['auth_method'] = '2fa'
            config['ssl_strict'] = True
        elif security_level == 'maximum':
            config['fail2ban'] = True
            config['auth_method'] = 'mfa'
            config['ssl_strict'] = True
            config['firewall'] = 'iptables'  # More control
        
        return config
    
    def _configure_backup(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure backup settings."""
        backup_pref = survey_data.get('backup_preference', {})
        
        config = {
            'enabled': backup_pref.get('strategy') != 'No automated backups',
            'strategy': backup_pref.get('strategy', 'Local backups only'),
            'frequency': backup_pref.get('frequency', 'Daily'),
            'retention': '30 days'
        }
        
        if config['strategy'] == 'Cloud backups':
            config['destinations'] = ['s3', 'backblaze']
        elif config['strategy'] == 'Both local and cloud':
            config['destinations'] = ['local', 's3']
        else:
            config['destinations'] = ['local']
        
        return config
    
    def _configure_monitoring(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configure monitoring settings."""
        monitoring = survey_data.get('monitoring', {})
        
        config = {
            'enabled': monitoring.get('level') != 'No monitoring',
            'solution': 'uptime-kuma',
            'alerts_enabled': monitoring.get('alerts', False),
            'alert_channels': monitoring.get('alert_methods', [])
        }
        
        if monitoring.get('level') == 'Full observability stack':
            config['solution'] = 'prometheus-grafana-loki'
        elif monitoring.get('level') == 'Detailed metrics and logs':
            config['solution'] = 'prometheus-grafana'
        
        return config


if __name__ == "__main__":
    # Test the recommender
    recommender = ServiceRecommender()
    
    # Sample data
    scan_data = {
        'environment': {
            'cpu_count': 4,
            'memory': {'available_gb': 8},
            'disk': {'free_gb': 100},
            'docker': {'installed': True}
        }
    }
    
    survey_data = {
        'primary_use': 'media_server',
        'media_details': {
            'content_type': ['Movies', 'TV Shows'],
            'transcoding': True
        },
        'security_level': 'enhanced',
        'monitoring': {
            'level': 'Basic uptime monitoring',
            'alerts': True
        },
        'backup_preference': {
            'strategy': 'Local backups only',
            'frequency': 'Daily'
        },
        'external_access': {
            'needed': True,
            'method': 'VPN (most secure)'
        }
    }
    
    recommendations = recommender.recommend(scan_data, survey_data)
    print(json.dumps(recommendations, indent=2))

#!/usr/bin/env python3
"""
Configuration Generator for Home-Lab Setup
Generates configuration files based on user preferences and system analysis
"""

import json
import os
import secrets
import string
from typing import Dict, List, Any
from jinja2 import Template
import yaml
from datetime import datetime
import ipaddress
import subprocess


class Configurator:
    """Generate configurations based on user input and system analysis"""
    
    def __init__(self):
        self.user_config = self._load_json('/tmp/user_config.json')
        self.network_scan = self._load_json('/tmp/network_scan.json')
        self.system_analysis = self._load_json('/tmp/system_analysis.json')
        self.security_audit = self._load_json('/tmp/security_audit.json')
        
        self.config_dir = "/home/user/workspace/Paradelala/config"
        self.generated_configs = []
        self.secrets = {}
    
    def _load_json(self, filepath: str) -> Dict:
        """Load JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def generate_password(self, length: int = 32) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_secrets(self):
        """Generate all required secrets"""
        print("Generating secrets...")
        
        self.secrets = {
            "postgres_password": self.generate_password(),
            "redis_password": self.generate_password(),
            "grafana_admin_password": self.generate_password(),
            "nextcloud_admin_password": self.generate_password(),
            "vaultwarden_admin_token": self.generate_password(48),
            "authelia_jwt_secret": self.generate_password(64),
            "authelia_session_secret": self.generate_password(64),
            "authelia_storage_encryption_key": self.generate_password(64),
            "wireguard_private_key": self._generate_wireguard_key(),
            "traefik_dashboard_password": self.generate_password()
        }
        
        # Save secrets securely
        secrets_file = os.path.join(self.config_dir, '.secrets.json')
        with open(secrets_file, 'w') as f:
            json.dump(self.secrets, f, indent=2)
        os.chmod(secrets_file, 0o600)
        
        print(f"Secrets saved to {secrets_file}")
    
    def _generate_wireguard_key(self) -> str:
        """Generate WireGuard private key"""
        try:
            result = subprocess.run(['wg', 'genkey'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        # Fallback to random key
        return self.generate_password(44)
    
    def generate_docker_compose(self):
        """Generate docker-compose.yml based on selected services"""
        print("Generating docker-compose.yml...")
        
        compose = {
            "version": "3.8",
            "services": {},
            "networks": {
                "homelab": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [{"subnet": "172.20.0.0/16"}]
                    }
                }
            },
            "volumes": {}
        }
        
        # Add selected services
        selected_services = self.user_config.get("services", {}).get("selected", [])
        
        # Nginx/Traefik reverse proxy
        if "nginx_proxy" in selected_services:
            compose["services"]["nginx"] = {
                "image": "nginx:alpine",
                "container_name": "nginx-proxy",
                "restart": "unless-stopped",
                "ports": [
                    "80:80",
                    "443:443"
                ],
                "volumes": [
                    "./nginx/nginx.conf:/etc/nginx/nginx.conf:ro",
                    "./nginx/conf.d:/etc/nginx/conf.d:ro",
                    "./nginx/ssl:/etc/nginx/ssl:ro",
                    "nginx-cache:/var/cache/nginx"
                ],
                "networks": ["homelab"],
                "logging": {
                    "driver": "json-file",
                    "options": {
                        "max-size": "10m",
                        "max-file": "3"
                    }
                }
            }
            compose["volumes"]["nginx-cache"] = {}
        
        elif "traefik" in selected_services:
            compose["services"]["traefik"] = {
                "image": "traefik:v2.10",
                "container_name": "traefik",
                "restart": "unless-stopped",
                "security_opt": ["no-new-privileges:true"],
                "ports": [
                    "80:80",
                    "443:443",
                    "8080:8080"
                ],
                "environment": {
                    "CF_API_EMAIL": self.user_config.get("basic_settings", {}).get("email", ""),
                    "CF_DNS_API_TOKEN": "${CF_DNS_API_TOKEN}"
                },
                "volumes": [
                    "/var/run/docker.sock:/var/run/docker.sock:ro",
                    "./traefik/traefik.yml:/traefik.yml:ro",
                    "./traefik/config.yml:/config.yml:ro",
                    "traefik-acme:/acme"
                ],
                "networks": ["homelab"],
                "labels": {
                    "traefik.enable": "true",
                    "traefik.http.routers.traefik.entrypoints": "http",
                    "traefik.http.routers.traefik.rule": "Host(`traefik.${DOMAIN}`)",
                    "traefik.http.routers.traefik-secure.entrypoints": "https",
                    "traefik.http.routers.traefik-secure.rule": "Host(`traefik.${DOMAIN}`)",
                    "traefik.http.routers.traefik-secure.tls": "true",
                    "traefik.http.routers.traefik-secure.service": "api@internal"
                }
            }
            compose["volumes"]["traefik-acme"] = {}
        
        # Monitoring stack
        if "prometheus" in selected_services:
            compose["services"]["prometheus"] = {
                "image": "prom/prometheus:latest",
                "container_name": "prometheus",
                "restart": "unless-stopped",
                "user": "nobody",
                "volumes": [
                    "./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                    "prometheus-data:/prometheus"
                ],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus",
                    "--web.console.libraries=/etc/prometheus/console_libraries",
                    "--web.console.templates=/etc/prometheus/consoles",
                    "--web.enable-lifecycle"
                ],
                "networks": ["homelab"],
                "labels": self._get_traefik_labels("prometheus", auth=True)
            }
            compose["volumes"]["prometheus-data"] = {}
            
            # Add node exporter
            compose["services"]["node-exporter"] = {
                "image": "prom/node-exporter:latest",
                "container_name": "node-exporter",
                "restart": "unless-stopped",
                "pid": "host",
                "volumes": [
                    "/proc:/host/proc:ro",
                    "/sys:/host/sys:ro",
                    "/:/rootfs:ro"
                ],
                "command": [
                    "--path.procfs=/host/proc",
                    "--path.rootfs=/rootfs",
                    "--path.sysfs=/host/sys",
                    "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)"
                ],
                "networks": ["homelab"]
            }
        
        if "grafana" in selected_services:
            compose["services"]["grafana"] = {
                "image": "grafana/grafana:latest",
                "container_name": "grafana",
                "restart": "unless-stopped",
                "user": "472",
                "environment": {
                    "GF_SECURITY_ADMIN_USER": "admin",
                    "GF_SECURITY_ADMIN_PASSWORD": self.secrets["grafana_admin_password"],
                    "GF_USERS_ALLOW_SIGN_UP": "false",
                    "GF_INSTALL_PLUGINS": "grafana-clock-panel,grafana-simple-json-datasource"
                },
                "volumes": [
                    "grafana-data:/var/lib/grafana",
                    "./grafana/provisioning:/etc/grafana/provisioning:ro"
                ],
                "networks": ["homelab"],
                "labels": self._get_traefik_labels("grafana")
            }
            compose["volumes"]["grafana-data"] = {}
        
        # Uptime Kuma
        if "uptime_kuma" in selected_services:
            compose["services"]["uptime-kuma"] = {
                "image": "louislam/uptime-kuma:latest",
                "container_name": "uptime-kuma",
                "restart": "unless-stopped",
                "volumes": [
                    "uptime-kuma-data:/app/data"
                ],
                "networks": ["homelab"],
                "labels": self._get_traefik_labels("status")
            }
            compose["volumes"]["uptime-kuma-data"] = {}
        
        # Storage services
        if "nextcloud" in selected_services:
            compose["services"]["nextcloud"] = {
                "image": "nextcloud:latest",
                "container_name": "nextcloud",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_HOST": "postgres",
                    "POSTGRES_DB": "nextcloud",
                    "POSTGRES_USER": "nextcloud",
                    "POSTGRES_PASSWORD": self.secrets["postgres_password"],
                    "NEXTCLOUD_ADMIN_USER": "admin",
                    "NEXTCLOUD_ADMIN_PASSWORD": self.secrets["nextcloud_admin_password"],
                    "NEXTCLOUD_TRUSTED_DOMAINS": self.user_config.get("basic_settings", {}).get("domain", "localhost")
                },
                "volumes": [
                    "nextcloud-data:/var/www/html"
                ],
                "networks": ["homelab"],
                "depends_on": ["postgres"],
                "labels": self._get_traefik_labels("cloud")
            }
            compose["volumes"]["nextcloud-data"] = {}
        
        # Security services
        if "vaultwarden" in selected_services:
            compose["services"]["vaultwarden"] = {
                "image": "vaultwarden/server:latest",
                "container_name": "vaultwarden",
                "restart": "unless-stopped",
                "environment": {
                    "DOMAIN": f"https://vault.{self.user_config.get('basic_settings', {}).get('domain', 'localhost')}",
                    "SIGNUPS_ALLOWED": "false",
                    "ADMIN_TOKEN": self.secrets["vaultwarden_admin_token"],
                    "WEBSOCKET_ENABLED": "true"
                },
                "volumes": [
                    "vaultwarden-data:/data"
                ],
                "networks": ["homelab"],
                "labels": self._get_traefik_labels("vault")
            }
            compose["volumes"]["vaultwarden-data"] = {}
        
        if "authelia" in selected_services:
            compose["services"]["authelia"] = {
                "image": "authelia/authelia:latest",
                "container_name": "authelia",
                "restart": "unless-stopped",
                "environment": {
                    "TZ": self.user_config.get("basic_settings", {}).get("timezone", "UTC")
                },
                "volumes": [
                    "./authelia:/config"
                ],
                "networks": ["homelab"],
                "labels": self._get_traefik_labels("auth")
            }
        
        # Databases
        if "postgresql" in selected_services or "nextcloud" in selected_services:
            compose["services"]["postgres"] = {
                "image": "postgres:15-alpine",
                "container_name": "postgres",
                "restart": "unless-stopped",
                "environment": {
                    "POSTGRES_PASSWORD": self.secrets["postgres_password"],
                    "POSTGRES_USER": "homelab",
                    "POSTGRES_DB": "homelab"
                },
                "volumes": [
                    "postgres-data:/var/lib/postgresql/data"
                ],
                "networks": ["homelab"]
            }
            compose["volumes"]["postgres-data"] = {}
        
        if "redis" in selected_services:
            compose["services"]["redis"] = {
                "image": "redis:7-alpine",
                "container_name": "redis",
                "restart": "unless-stopped",
                "command": f"redis-server --requirepass {self.secrets['redis_password']}",
                "volumes": [
                    "redis-data:/data"
                ],
                "networks": ["homelab"]
            }
            compose["volumes"]["redis-data"] = {}
        
        # Pi-hole
        if self.user_config.get("networking", {}).get("use_pihole"):
            compose["services"]["pihole"] = {
                "image": "pihole/pihole:latest",
                "container_name": "pihole",
                "restart": "unless-stopped",
                "hostname": "pihole",
                "environment": {
                    "TZ": self.user_config.get("basic_settings", {}).get("timezone", "UTC"),
                    "WEBPASSWORD": self.generate_password(16),
                    "PIHOLE_DNS_": "1.1.1.1;1.0.0.1"
                },
                "volumes": [
                    "pihole-etc:/etc/pihole",
                    "pihole-dnsmasq:/etc/dnsmasq.d"
                ],
                "ports": [
                    "53:53/tcp",
                    "53:53/udp"
                ],
                "networks": ["homelab"],
                "labels": self._get_traefik_labels("pihole", port=80)
            }
            compose["volumes"]["pihole-etc"] = {}
            compose["volumes"]["pihole-dnsmasq"] = {}
        
        # Add resource limits if enabled
        if self.user_config.get("advanced", {}).get("enable_resource_limits"):
            for service in compose["services"].values():
                if "deploy" not in service:
                    service["deploy"] = {}
                service["deploy"]["resources"] = {
                    "limits": {
                        "cpus": "0.5",
                        "memory": "512M"
                    }
                }
        
        # Save docker-compose.yml
        compose_file = os.path.join(self.config_dir, "docker-compose.yml")
        with open(compose_file, 'w') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
        
        self.generated_configs.append(compose_file)
        print(f"Generated {compose_file}")
    
    def _get_traefik_labels(self, service: str, auth: bool = False, port: int = None) -> Dict[str, str]:
        """Generate Traefik labels for a service"""
        domain = self.user_config.get("basic_settings", {}).get("domain", "localhost")
        labels = {
            "traefik.enable": "true",
            f"traefik.http.routers.{service}.entrypoints": "http",
            f"traefik.http.routers.{service}.rule": f"Host(`{service}.{domain}`)",
            f"traefik.http.middlewares.{service}-https-redirect.redirectscheme.scheme": "https",
            f"traefik.http.routers.{service}.middlewares": f"{service}-https-redirect",
            f"traefik.http.routers.{service}-secure.entrypoints": "https",
            f"traefik.http.routers.{service}-secure.rule": f"Host(`{service}.{domain}`)",
            f"traefik.http.routers.{service}-secure.tls": "true",
            f"traefik.http.routers.{service}-secure.tls.certresolver": "cloudflare"
        }
        
        if port:
            labels[f"traefik.http.services.{service}.loadbalancer.server.port"] = str(port)
        
        if auth:
            labels[f"traefik.http.routers.{service}-secure.middlewares"] = "authelia@docker"
        
        return labels
    
    def generate_backup_script(self):
        """Generate backup script"""
        if not self.user_config.get("backup", {}).get("enable_backups"):
            return
        
        print("Generating backup script...")
        
        backup_script = """#!/bin/bash
# Automated backup script for home-lab

set -euo pipefail

# Configuration
BACKUP_DIR="/backup"
RETENTION_DAYS={retention_days}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/homelab-backup.log"

# Logging function
log() {{
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}}

log "Starting backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Backup Docker volumes
log "Backing up Docker volumes..."
for volume in $(docker volume ls -q); do
    log "Backing up volume: $volume"
    docker run --rm -v "$volume:/data" -v "$BACKUP_DIR/$TIMESTAMP:/backup" \
        alpine tar czf "/backup/$volume.tar.gz" -C /data .
done

# Backup configuration files
log "Backing up configuration files..."
tar czf "$BACKUP_DIR/$TIMESTAMP/config.tar.gz" -C /home/user/workspace/Paradelala config/

# Backup database dumps
if docker ps | grep -q postgres; then
    log "Backing up PostgreSQL databases..."
    docker exec postgres pg_dumpall -U homelab > "$BACKUP_DIR/$TIMESTAMP/postgres_dump.sql"
fi

# Clean old backups
log "Cleaning old backups..."
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {{}} \;

# Upload to S3 if configured
if [[ -n "${{S3_BUCKET:-}}" ]]; then
    log "Uploading to S3..."
    aws s3 sync "$BACKUP_DIR/$TIMESTAMP" "s3://$S3_BUCKET/homelab-backup/$TIMESTAMP/"
fi

log "Backup completed successfully!"
""".format(retention_days=self.user_config.get("backup", {}).get("retention_days", 7))
        
        backup_script_path = os.path.join(self.config_dir, "backup.sh")
        with open(backup_script_path, 'w') as f:
            f.write(backup_script)
        os.chmod(backup_script_path, 0o755)
        
        self.generated_configs.append(backup_script_path)
        print(f"Generated {backup_script_path}")
    
    def generate_all_configurations(self):
        """Generate all configuration files"""
        print("\nGenerating all configurations...")
        
        # Create config directory
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Generate configurations
        self.generate_secrets()
        self.generate_docker_compose()
        self.generate_nginx_config()
        self.generate_traefik_config()
        self.generate_prometheus_config()
        self.generate_wireguard_config()
        self.generate_env_file()
        self.generate_backup_script()
        
        print("\nConfiguration generation completed!")
        print(f"\nGenerated files:")
        for config in self.generated_configs:
            print(f"  - {config}")
        
        return True


def main():
    """Main entry point"""
    configurator = Configurator()
    success = configurator.generate_all_configurations()
    
    if success:
        print("\nConfigurations generated successfully!")
        print("Next step: Run the installation script to deploy your home-lab.")
    else:
        print("\nConfiguration generation failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

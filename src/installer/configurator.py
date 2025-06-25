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

    def _generate_swag_service(self) -> str:
        """Generate SWAG reverse proxy service configuration"""
        return """
  swag:
    image: lscr.io/linuxserver/swag:latest
    container_name: swag
    cap_add:
      - NET_ADMIN
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=${TZ}
      - URL=${DOMAIN}
      - SUBDOMAINS=wildcard
      - VALIDATION=http
      - EMAIL=${EMAIL}
    volumes:
      - ./config/swag:/config
    ports:
      - 443:443
      - 80:80
    restart: unless-stopped
    networks:
      - homelab

  heimdall:
    image: lscr.io/linuxserver/heimdall:latest
    container_name: heimdall
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=${TZ}
    volumes:
      - ./config/heimdall:/config
    ports:
      - 8080:80
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_heimdall_service(self) -> str:
        """Generate Heimdall dashboard service configuration"""
        return """
  heimdall:
    image: lscr.io/linuxserver/heimdall:latest
    container_name: heimdall
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=${TZ}
    volumes:
      - ./config/heimdall:/config
    ports:
      - 8080:80
    restart: unless-stopped
    networks:
      - homelab
"""


    def _generate_nginx_service(self) -> str:
        """Generate Nginx reverse proxy service"""
        return """
  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx:/etc/nginx/conf.d
      - ./config/ssl:/etc/ssl/certs
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_caddy_service(self) -> str:
        """Generate Caddy reverse proxy service"""
        return """
  caddy:
    image: caddy:alpine
    container_name: caddy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/caddy/Caddyfile:/etc/caddy/Caddyfile
      - ./config/caddy/data:/data
      - ./config/caddy/config:/config
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_traefik_service(self) -> str:
        """Generate Traefik reverse proxy service"""
        return """
  traefik:
    image: traefik:v2.9
    container_name: traefik
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - ./config/traefik:/etc/traefik
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_prometheus_service(self) -> str:
        """Generate Prometheus monitoring service"""
        return """
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_grafana_service(self) -> str:
        """Generate Grafana dashboard service"""
        return """
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_portainer_service(self) -> str:
        """Generate Portainer container management service"""
        return """
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_pihole_service(self) -> str:
        """Generate Pi-hole DNS service"""
        return """
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "8053:80/tcp"
    environment:
      - TZ=${TZ}
      - WEBPASSWORD=${PIHOLE_PASSWORD}
    volumes:
      - ./config/pihole/etc:/etc/pihole
      - ./config/pihole/dnsmasq:/etc/dnsmasq.d
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_nextcloud_service(self) -> str:
        """Generate Nextcloud file sharing service"""
        return """
  nextcloud:
    image: nextcloud:apache
    container_name: nextcloud
    ports:
      - "8081:80"
    environment:
      - NEXTCLOUD_ADMIN_USER=admin
      - NEXTCLOUD_ADMIN_PASSWORD=${NEXTCLOUD_PASSWORD}
    volumes:
      - nextcloud_data:/var/www/html
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_gitlab_service(self) -> str:
        """Generate GitLab service"""
        return """
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    ports:
      - "8082:80"
      - "2222:22"
    environment:
      - GITLAB_ROOT_PASSWORD=${GITLAB_PASSWORD}
    volumes:
      - gitlab_data:/var/opt/gitlab
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_vault_service(self) -> str:
        """Generate HashiCorp Vault service"""
        return """
  vault:
    image: vault:latest
    container_name: vault
    ports:
      - "8200:8200"
    environment:
      - VAULT_DEV_ROOT_TOKEN_ID=${VAULT_TOKEN}
    volumes:
      - vault_data:/vault/data
    restart: unless-stopped
    networks:
      - homelab
"""

    
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
    

    def _generate_swag_service(self) -> str:
        """Generate SWAG reverse proxy service configuration"""
        return """
  swag:
    image: lscr.io/linuxserver/swag:latest
    container_name: swag
    cap_add:
      - NET_ADMIN
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=${TZ}
      - URL=${DOMAIN}
      - SUBDOMAINS=wildcard
      - VALIDATION=http
      - EMAIL=${EMAIL}
    volumes:
      - ./config/swag:/config
    ports:
      - 443:443
      - 80:80
    restart: unless-stopped
    networks:
      - homelab
"""

    def _generate_heimdall_service(self) -> str:
        """Generate Heimdall dashboard service configuration"""
        return """
  heimdall:
    image: lscr.io/linuxserver/heimdall:latest
    container_name: heimdall
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=${TZ}
    volumes:
      - ./config/heimdall:/config
    ports:
      - 8080:80
    restart: unless-stopped
    networks:
      - homelab
"""

    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml content"""
        services = []
        
        # Base services
        services.append("""
version: '3.8'

services:""")
        
        # Add reverse proxy (SWAG or others)
        if self.user_config.get('enable_swag', False):
            services.append(self._generate_swag_service())
        elif self.user_config.get('enable_reverse_proxy', False):
            proxy_type = self.user_config.get('proxy_type', 'nginx')
            if proxy_type == 'nginx':
                services.append(self._generate_nginx_service())
            elif proxy_type == 'caddy':
                services.append(self._generate_caddy_service())
            elif proxy_type == 'traefik':
                services.append(self._generate_traefik_service())
        
        # Add Heimdall dashboard
        if self.user_config.get('enable_heimdall', False):
            services.append(self._generate_heimdall_service())
        
        # Add monitoring services
        if self.user_config.get('enable_monitoring', False):
            services.append(self._generate_prometheus_service())
            services.append(self._generate_grafana_service())
        
        # Add application services
        if self.user_config.get('enable_portainer', False):
            services.append(self._generate_portainer_service())
        
        if self.user_config.get('enable_pihole', False):
            services.append(self._generate_pihole_service())
        
        if self.user_config.get('enable_nextcloud', False):
            services.append(self._generate_nextcloud_service())
        
        if self.user_config.get('enable_gitlab', False):
            services.append(self._generate_gitlab_service())
        
        if self.user_config.get('enable_vault', False):
            services.append(self._generate_vault_service())
        
        # Add networks
        services.append("""
networks:
  homelab:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  portainer_data:
  nextcloud_data:
  gitlab_data:
  vault_data:""")
        
        return '\n'.join(services)
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

#!/usr/bin/env python3
"""
Tunnel Manager Module
Manages secure tunneling and proxy configurations for home server connections.
"""

import os
import subprocess
import json
import yaml
import ipaddress
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from rich.console import Console


class TunnelManager:
    """Manages tunnel and proxy configurations."""
    
    def __init__(self):
        self.console = Console()
        self.config_dir = Path("/opt/homelab/configs/tunnel")
        self.wireguard_dir = Path("/opt/homelab/configs/wireguard")
        
    def setup(self, proxy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup tunnel based on configuration."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            tunnel_type = proxy_config.get('tunnel_type', 'reverse_proxy')
            
            if tunnel_type == 'wireguard':
                return self._setup_wireguard()
            elif tunnel_type == 'cloudflare':
                return self._setup_cloudflare_tunnel()
            elif tunnel_type == 'reverse_proxy':
                return self._setup_reverse_proxy(proxy_config)
            else:
                return self._setup_basic_proxy()
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _setup_wireguard(self) -> Dict[str, Any]:
        """Setup WireGuard VPN tunnel."""
        self.console.print("[cyan]Setting up WireGuard VPN...[/cyan]")
        
        self.wireguard_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate server keys
        server_private_key = self._generate_wireguard_key()
        server_public_key = self._get_wireguard_public_key(server_private_key)
        
        # Generate client configurations
        clients = []
        for i in range(5):  # Generate 5 client configs
            client = self._generate_wireguard_client(i + 1, server_public_key)
            clients.append(client)
        
        # Create server configuration
        server_config = self._create_wireguard_server_config(server_private_key, clients)
        
        # Save configurations
        server_config_path = self.wireguard_dir / "wg0.conf"
        with open(server_config_path, 'w') as f:
            f.write(server_config)
        
        # Save client configurations
        for i, client in enumerate(clients):
            client_config_path = self.wireguard_dir / f"client{i+1}.conf"
            with open(client_config_path, 'w') as f:
                f.write(client['config'])
        
        # Generate QR codes for mobile clients
        self._generate_wireguard_qr_codes(clients)
        
        return {
            'success': True,
            'vpn_config_path': str(self.wireguard_dir),
            'public_endpoint': f"{self._get_public_ip()}:51820",
            'client_configs': [f"client{i+1}.conf" for i in range(len(clients))]
        }
    
    def _setup_cloudflare_tunnel(self) -> Dict[str, Any]:
        """Setup Cloudflare Tunnel (Argo Tunnel)."""
        self.console.print("[cyan]Setting up Cloudflare Tunnel...[/cyan]")
        
        # Create cloudflared configuration
        config = {
            'tunnel': 'homelab-tunnel',
            'credentials-file': '/opt/homelab/configs/tunnel/credentials.json',
            'ingress': [
                {
                    'hostname': 'homelab.example.com',
                    'service': 'http://nginx-proxy-manager:80'
                },
                {
                    'hostname': 'media.example.com',
                    'service': 'http://jellyfin:8096'
                },
                {
                    'service': 'http_status:404'
                }
            ]
        }
        
        config_path = self.config_dir / "cloudflared.yml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        # Create Docker service for cloudflared
        cloudflared_compose = {
            'version': '3.8',
            'services': {
                'cloudflared': {
                    'image': 'cloudflare/cloudflared:latest',
                    'container_name': 'cloudflared',
                    'command': 'tunnel --config /etc/cloudflared/config.yml run',
                    'volumes': [
                        f'{self.config_dir}:/etc/cloudflared:ro'
                    ],
                    'restart': 'unless-stopped',
                    'networks': ['homelab']
                }
            }
        }
        
        compose_path = self.config_dir / "cloudflared-compose.yml"
        with open(compose_path, 'w') as f:
            yaml.dump(cloudflared_compose, f)
        
        return {
            'success': True,
            'vpn_config_path': str(config_path),
            'public_endpoint': 'https://homelab.example.com',
            'setup_instructions': [
                "1. Install cloudflared on your system",
                "2. Run: cloudflared tunnel login",
                "3. Create tunnel: cloudflared tunnel create homelab-tunnel",
                "4. Copy the credentials.json to /opt/homelab/configs/tunnel/",
                "5. Update the hostnames in the configuration",
                "6. Start the tunnel service"
            ]
        }
    
    def _setup_reverse_proxy(self, proxy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup reverse proxy with authentication."""
        self.console.print("[cyan]Setting up secure reverse proxy...[/cyan]")
        
        # Create Nginx configuration for reverse proxy
        nginx_config = self._create_nginx_reverse_proxy_config(proxy_config)
        
        config_path = self.config_dir / "nginx-reverse-proxy.conf"
        with open(config_path, 'w') as f:
            f.write(nginx_config)
        
        # Setup SSL certificates
        ssl_config = self._setup_ssl_certificates()
        
        # Setup authentication if required
        if proxy_config.get('auth_required'):
            auth_config = self._setup_authentication()
        else:
            auth_config = None
        
        return {
            'success': True,
            'vpn_config_path': str(config_path),
            'public_endpoint': f"https://{self._get_domain()}",
            'ssl_config': ssl_config,
            'auth_config': auth_config
        }
    
    def _setup_basic_proxy(self) -> Dict[str, Any]:
        """Setup basic proxy without additional security."""
        self.console.print("[cyan]Setting up basic proxy...[/cyan]")
        
        return {
            'success': True,
            'vpn_config_path': 'N/A',
            'public_endpoint': f"http://{self._get_public_ip()}",
            'warning': 'Basic proxy without encryption - not recommended for production'
        }
    
    def _generate_wireguard_key(self) -> str:
        """Generate WireGuard private key."""
        try:
            result = subprocess.run(['wg', 'genkey'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            # Fallback to generating a random key
            return secrets.token_urlsafe(32)
    
    def _get_wireguard_public_key(self, private_key: str) -> str:
        """Get WireGuard public key from private key."""
        try:
            result = subprocess.run(
                ['wg', 'pubkey'],
                input=private_key,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            # Fallback
            return secrets.token_urlsafe(32)
    
    def _generate_wireguard_client(self, client_id: int, server_public_key: str) -> Dict[str, Any]:
        """Generate WireGuard client configuration."""
        client_private_key = self._generate_wireguard_key()
        client_public_key = self._get_wireguard_public_key(client_private_key)
        client_ip = f"10.13.13.{client_id + 1}"
        
        client_config = f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_ip}/32
DNS = 10.13.13.1

[Peer]
PublicKey = {server_public_key}
Endpoint = {self._get_public_ip()}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
        
        return {
            'id': client_id,
            'public_key': client_public_key,
            'ip': client_ip,
            'config': client_config
        }
    
    def _create_wireguard_server_config(self, server_private_key: str, clients: List[Dict[str, Any]]) -> str:
        """Create WireGuard server configuration."""
        config = f"""[Interface]
PrivateKey = {server_private_key}
Address = 10.13.13.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

"""
        
        for client in clients:
            config += f"""
[Peer]
PublicKey = {client['public_key']}
AllowedIPs = {client['ip']}/32
"""
        
        return config
    
    def _generate_wireguard_qr_codes(self, clients: List[Dict[str, Any]]):
        """Generate QR codes for WireGuard client configurations."""
        try:
            import qrcode
            
            qr_dir = self.wireguard_dir / "qr_codes"
            qr_dir.mkdir(exist_ok=True)
            
            for client in clients:
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(client['config'])
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(qr_dir / f"client{client['id']}_qr.png")
        except ImportError:
            self.console.print("[yellow]QR code generation skipped (qrcode module not installed)[/yellow]")
    
    def _create_nginx_reverse_proxy_config(self, proxy_config: Dict[str, Any]) -> str:
        """Create Nginx reverse proxy configuration."""
        ssl_config = """
    ssl_certificate /etc/letsencrypt/live/homelab.local/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/homelab.local/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
""" if proxy_config.get('ssl_provider') == 'letsencrypt' else ""
        
        auth_config = """
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
""" if proxy_config.get('auth_required') else ""
        
        config = f"""
server {{
    listen 80;
    server_name {self._get_domain()};
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {self._get_domain()};
    
{ssl_config}
{auth_config}
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Proxy settings
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Service locations
    location / {{
        proxy_pass http://nginx-proxy-manager:81;
    }}
    
    location /jellyfin {{
        proxy_pass http://jellyfin:8096;
    }}
    
    location /gitea {{
        proxy_pass http://gitea:3000;
    }}
    
    location /homeassistant {{
        proxy_pass http://homeassistant:8123;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
"""
        return config
    
    def _setup_ssl_certificates(self) -> Dict[str, Any]:
        """Setup SSL certificates."""
        # In a real implementation, this would use certbot or similar
        return {
            'provider': 'letsencrypt',
            'domain': self._get_domain(),
            'auto_renew': True
        }
    
    def _setup_authentication(self) -> Dict[str, Any]:
        """Setup authentication for reverse proxy."""
        # In a real implementation, this would set up OAuth2, Authelia, etc.
        return {
            'method': 'basic_auth',
            'users': ['admin'],
            'config_path': '/etc/nginx/.htpasswd'
        }
    
    def _get_public_ip(self) -> str:
        """Get public IP address."""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            return "YOUR_PUBLIC_IP"
    
    def _get_domain(self) -> str:
        """Get domain name."""
        # In a real implementation, this would be configured
        return "homelab.local"


if __name__ == "__main__":
    # Test the tunnel manager
    manager = TunnelManager()
    result = manager.setup({'tunnel_type': 'wireguard'})
    print(json.dumps(result, indent=2))

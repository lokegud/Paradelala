# Secure Home-Lab Setup

A comprehensive, AI-powered solution for setting up a private and secure home-lab environment on a VPS with proxy capabilities to home servers.

## 🚀 Features

- **AI-Powered Setup**: Intelligent agents scan your environment and recommend optimal configurations
- **Security First**: Industry best practices with automated security hardening
- **Interactive Installation**: User-friendly questionnaire to customize your setup
- **Modular Architecture**: Choose only the services you need
- **Automated Backups**: Built-in backup solutions with multiple destination support
- **Monitoring & Alerting**: Comprehensive monitoring stack with customizable alerts
- **VPN Access**: Secure remote access via WireGuard
- **Reverse Proxy**: Choice of Nginx or Traefik with automatic SSL

## 📋 Requirements

- **Operating System**: Ubuntu 20.04+ or Debian 11+
- **RAM**: Minimum 1GB (2GB+ recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 1+ cores (2+ recommended)
- **Network**: Public IP address
- **Privileges**: Root or sudo access

## 🛠️ Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/secure-homelab.git
   cd secure-homelab
   ```

2. **Run the installer**:
   ```bash
   sudo bash scripts/install.sh
   ```

3. **Follow the interactive setup wizard**

## 📦 Available Services

### Core Services
- **Reverse Proxy**: Nginx or Traefik
- **VPN**: WireGuard for secure remote access
- **Firewall**: UFW with fail2ban
- **DNS**: Pi-hole for ad blocking and local DNS

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Beautiful dashboards
- **Uptime Kuma**: Simple uptime monitoring
- **Node Exporter**: System metrics

### Storage & Backup
- **Nextcloud**: Self-hosted cloud storage
- **MinIO**: S3-compatible object storage
- **Restic**: Automated backups

### Security & Authentication
- **Vaultwarden**: Password manager (Bitwarden compatible)
- **Authelia**: Single sign-on with 2FA

### Development Tools
- **Gitea**: Lightweight Git hosting
- **Drone CI**: Container-native CI/CD

### Databases
- **PostgreSQL**: Relational database
- **Redis**: In-memory data store

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   Cloudflare   │ (Optional)
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │  VPS Firewall  │
         │   (UFW/IPT)    │
         └────────┬───────┘
                  │
                  ▼
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────┐              ┌──────────┐
│ HTTP/S  │              │WireGuard │
│ :80/:443│              │  :51820  │
└────┬────┘              └────┬─────┘
     │                         │
     ▼                         ▼
┌─────────────────────────────────────┐
│        Reverse Proxy                │
│    (Nginx/Traefik + SSL)           │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│         Docker Network              │
│  ┌─────────┐ ┌─────────┐ ┌───────┐ │
│  │Services │ │Database │ │Monitor│ │
│  └─────────┘ └─────────┘ └───────┘ │
└─────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DOMAIN=your-domain.com
EMAIL=admin@your-domain.com
TZ=UTC
```

### Service Configuration
All service configurations are stored in the `config/` directory:
- `docker-compose.yml`: Container orchestration
- `nginx/`: Nginx configuration files
- `prometheus/`: Monitoring configuration
- `wireguard/`: VPN configuration

### Secrets Management
Secrets are automatically generated and stored in `config/.secrets.json` with restricted permissions.

## 🔒 Security Features

- **Automated Security Hardening**:
  - SSH hardening (key-only auth, non-standard port)
  - Firewall configuration with minimal exposed ports
  - Fail2ban for brute-force protection
  - Automatic security updates

- **Network Security**:
  - All services behind reverse proxy
  - SSL/TLS encryption with Let's Encrypt
  - Optional Cloudflare tunnel support
  - Isolated Docker networks

- **Access Control**:
  - WireGuard VPN for secure remote access
  - Optional SSO with Authelia
  - Service-level authentication

## 📊 Monitoring

The setup includes a comprehensive monitoring stack:

- **System Metrics**: CPU, memory, disk, network
- **Service Health**: Uptime monitoring for all services
- **Alerts**: Email, Discord, or Telegram notifications
- **Dashboards**: Pre-configured Grafana dashboards

## 💾 Backup Strategy

Automated backups with multiple destination support:
- Local backups with configurable retention
- S3-compatible storage support
- Scheduled via cron
- Database dumps included

## 🚨 Troubleshooting

### Common Issues

1. **Installation fails with permission errors**:
   ```bash
   sudo bash scripts/install.sh
   ```

2. **Services not accessible**:
   - Check firewall rules: `sudo ufw status`
   - Verify DNS records point to your VPS
   - Check service logs: `docker-compose logs <service>`

3. **SSL certificate issues**:
   - Ensure domain DNS is properly configured
   - Check Let's Encrypt rate limits
   - Verify email address is valid

### Logs

- Installation logs: `/var/log/homelab-setup.log`
- Service logs: `docker-compose logs -f <service>`
- System logs: `journalctl -u docker`

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with industry best practices
- Inspired by the self-hosting community
- Uses open-source software throughout

## 📞 Support

- **Documentation**: Check the [Wiki](https://github.com/yourusername/secure-homelab/wiki)
- **Issues**: Open an [issue](https://github.com/yourusername/secure-homelab/issues)
- **Discussions**: Join our [community](https://github.com/yourusername/secure-homelab/discussions)

---

**Note**: This is an active project. Always backup your data before making changes.

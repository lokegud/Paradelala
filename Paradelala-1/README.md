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

- **Operating System**: Ubuntu 22.04 LTS or Debian 11+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: Minimum 40GB free space
- **CPU**: 2+ cores recommended
- **Network**: Public IP address
- **Domain**: Required for SSL and services
- **Privileges**: Root or sudo access

For detailed requirements and setup instructions, see our comprehensive documentation:
- [System Overview](docs/SYSTEM_OVERVIEW.md) - Complete system architecture and components
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Step-by-step deployment instructions
- [SWAG & Heimdall Guide](docs/SWAG_HEIMDALL_GUIDE.md) - Reverse proxy and dashboard setup
- [VPS Hosting Guide](docs/VPS_HOSTING_GUIDE.md) - VPS provider recommendations and setup

## �️ Quick Start

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
- **SWAG**: Secure Web Application Gateway with automatic SSL
- **Authelia**: Single Sign-On and 2FA for all services
- **SearXNG**: Private meta search engine
- **Matrix Synapse**: Secure, decentralized chat platform
- **Redis**: Session management and caching
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
- **Authelia**: Comprehensive SSO solution with:
  - Two-factor authentication (2FA)
  - Access control policies
  - Brute-force protection
  - Session management

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
┌─────────────────────────────┐
│           SWAG              │
│    (Reverse Proxy + SSL)    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│         Authelia            │
│    (Authentication/SSO)     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│              Docker Network                  │
├───────────┬───────────┬────────────┬────────┤
│           │           │            │        │
▼           ▼           ▼            ▼        ▼
┌────────┐  ┌────────┐  ┌─────────┐  ┌────────┐
│SearXNG │  │ Matrix │  │ Redis   │  │Other   │
│Search  │  │Synapse │  │Sessions │  │Services│
└────────┘  └────────┘  └─────────┘  └────────┘
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
DOMAIN=your-domain.com
EMAIL=admin@your-domain.com
TZ=UTC
REDIS_PASSWORD=your-secure-password
MATRIX_REGISTRATION_SECRET=your-registration-secret
SEARXNG_SECRET=your-instance-secret
```

### Service Configuration
All service configurations are stored in the `config/` directory:

#### Authentication (Authelia)
- `config/authelia/configuration.yml`: Main Authelia configuration
- `config/authelia/users_database.yml`: User credentials and access rules

#### Reverse Proxy (SWAG)
- `config/swag/nginx/proxy-confs/`: Service-specific proxy configurations
- `config/swag/nginx/authelia-location.conf`: Authelia authentication middleware

#### Search Engine (SearXNG)
- `config/searxng/settings.yml`: Search engine configuration and preferences

#### Chat Platform (Matrix Synapse)
- `config/synapse/homeserver.yaml`: Matrix server configuration

### Secrets Management
- Secrets are automatically generated during installation
- Stored securely in `config/.secrets.json` with restricted permissions (0600)
- Include:
  - Authentication keys
  - Service passwords
  - Registration tokens
  - Encryption keys

## 🔒 Security Features

- **Authentication & Access Control**:
  - Single Sign-On (SSO) with Authelia
  - Two-factor authentication (2FA) support
  - Granular access control policies
  - Brute-force protection
  - Session management with Redis
  - User activity logging

- **Network Security**:
  - SWAG reverse proxy with automatic SSL/TLS
  - HTTP security headers (HSTS, CSP, etc.)
  - Fail2ban integration for brute-force protection
  - Isolated Docker networks for service separation
  - Optional Cloudflare integration
  - Regular security updates

- **Data Protection**:
  - Encrypted storage for sensitive data
  - Secure secret management
  - Regular automated backups
  - Matrix end-to-end encryption
  - SearXNG privacy-focused search

- **System Hardening**:
  - Minimal exposed ports (80/443 only)
  - Principle of least privilege
  - Regular security audits
  - Automated security updates
  - SSH hardening (key-only auth)

## 📊 Monitoring & Maintenance

### System Monitoring
- **Service Health Checks**:
  - Automatic container health monitoring
  - SSL certificate expiration checks
  - Authentication service status
  - Matrix federation status
  - Search engine availability

- **Resource Monitoring**:
  - Container resource usage
  - System metrics (CPU, memory, disk, network)
  - Redis session store status
  - Network connectivity checks

- **Security Monitoring**:
  - Authentication attempts logging
  - Failed login monitoring
  - Brute-force attempt detection
  - SSL/TLS configuration validation

### Automated Maintenance
- **Daily Tasks**:
  - Service health checks
  - Log rotation
  - Temporary file cleanup
  - Security scan

- **Weekly Tasks**:
  - Full backup creation
  - SSL certificate verification
  - Docker image updates
  - Security patches

- **Monthly Tasks**:
  - Full system updates
  - Backup verification
  - Performance optimization
  - Security audit

## 💾 Backup & Recovery

### Automated Backup System
- **Backup Contents**:
  - Service configurations
  - User data and preferences
  - Matrix Synapse chat history
  - Authentication database
  - SSL certificates
  - Docker volumes

- **Backup Features**:
  - Configurable retention policy
  - Compression and encryption
  - Incremental backups
  - Multiple destination support
    * Local storage
    * Remote servers (SCP/SFTP)
    * S3-compatible storage
    * Optional cloud backup

- **Recovery Procedures**:
  - Documented recovery process
  - Test restoration procedures
  - Point-in-time recovery options
  - Service-specific restoration

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Issues**:
   - **Authelia not working**:
     ```bash
     # Check Authelia logs
     docker-compose logs authelia
     # Verify Redis connection
     docker exec -it redis redis-cli ping
     ```
   - **2FA problems**:
     - Verify time synchronization
     - Check user configuration in users_database.yml
     - Reset 2FA if needed: `docker exec -it authelia authelia crypto hash --password 'newpassword'`

2. **Service Access Problems**:
   - **SWAG/SSL Issues**:
     ```bash
     # Check SWAG logs
     docker-compose logs swag
     # Verify SSL certificates
     docker exec swag openssl x509 -in /config/etc/letsencrypt/live/yourdomain.com/cert.pem -text
     ```
   - **DNS Configuration**:
     - Verify A records for all subdomains
     - Check DNS propagation: `dig +short yourdomain.com`
     - Confirm Cloudflare settings if used

3. **Matrix Synapse Issues**:
   - **Federation Problems**:
     ```bash
     # Check federation status
     curl -sL https://matrix.org/federationtester/api/report?server_name=yourdomain.com
     # View Synapse logs
     docker-compose logs synapse
     ```
   - **Database Issues**:
     - Check SQLite database integrity
     - Monitor storage space
     - Review media repository size

4. **SearXNG Problems**:
   - **Search Failures**:
     ```bash
     # Check SearXNG logs
     docker-compose logs searxng
     # Verify settings
     docker exec -it searxng cat /etc/searxng/settings.yml
     ```
   - **Performance Issues**:
     - Review rate limits
     - Check upstream search engine status
     - Monitor resource usage

### Log Locations

#### System Logs
- Installation: `/var/log/homelab-setup.log`
- Docker: `journalctl -u docker`
- UFW Firewall: `/var/log/ufw.log`

#### Service Logs
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs -f [service]
# Examples:
docker-compose logs -f swag
docker-compose logs -f authelia
docker-compose logs -f matrix-synapse
docker-compose logs -f searxng
```

#### Authentication Logs
- Authelia: `/config/authelia/authelia.log`
- SWAG Access: `/config/swag/log/nginx/access.log`
- SWAG Error: `/config/swag/log/nginx/error.log`

### Quick Fixes

1. **Reset Service**:
   ```bash
   docker-compose restart [service]
   ```

2. **Clear Redis Cache**:
   ```bash
   docker exec -it redis redis-cli FLUSHALL
   ```

3. **Rebuild Service**:
   ```bash
   docker-compose up -d --force-recreate [service]
   ```

4. **Verify Configurations**:
   ```bash
   # Test SWAG config
   docker exec swag nginx -t
   
   # Check Authelia config
   docker exec authelia authelia validate-config
   ```

### Prevention & Maintenance

1. **Regular Checks**:
   ```bash
   # Run verification script
   ./scripts/verify_deployment.sh
   
   # Check service health
   docker-compose ps
   ```

2. **Backup Before Changes**:
   ```bash
   # Create backup
   ./scripts/backup.sh
   ```

3. **Monitor Resources**:
   ```bash
   # Check container stats
   docker stats
   
   # View disk usage
   ncdu /config
   ```

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

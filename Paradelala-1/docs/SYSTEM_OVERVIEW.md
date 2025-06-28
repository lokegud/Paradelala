# Secure Home-Lab System Overview

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Core Services](#core-services)
4. [Security Features](#security-features)
5. [Requirements](#requirements)
6. [Installation Process](#installation-process)
7. [Service Configuration](#service-configuration)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)

## Introduction

This secure home-lab setup provides a comprehensive, self-hosted infrastructure with emphasis on privacy, security, and ease of management. It combines various open-source services into a cohesive system, all managed through Docker containers and secured with modern authentication methods.

## System Architecture

### Core Components
- **SWAG (Secure Web Application Gateway)**: Handles SSL/TLS termination and reverse proxy
- **Authelia**: Provides Single Sign-On (SSO) and 2FA for all services
- **Redis**: Session store for Authelia
- **Docker & Docker Compose**: Container management and orchestration

### Network Architecture
```
                                   ┌─────────────┐
                                   │    SWAG     │
                                   │ Reverse Proxy│
                                   └──────┬──────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │                    │                    │
               ┌─────┴─────┐       ┌─────┴─────┐        ┌─────┴─────┐
               │  Authelia  │       │  SearXNG  │        │   Matrix  │
               │    SSO     │       │  Search   │        │  Synapse  │
               └─────┬─────┘       └───────────┘        └───────────┘
                     │
               ┌─────┴─────┐
               │   Redis   │
               │  Sessions │
               └───────────┘
```

## Core Services

### 1. Authentication & Security
- **Authelia**
  - Single Sign-On (SSO) provider
  - Two-factor authentication (2FA)
  - Access control for all services
  - Requirements:
    * Redis for session storage
    * Configuration in `/config/authelia/`
    * Minimum 1GB RAM

### 2. Search & Privacy
- **SearXNG**
  - Private meta search engine
  - No tracking or logging
  - Customizable search sources
  - Requirements:
    * Configuration in `/config/searxng/`
    * Minimum 512MB RAM

### 3. Communication
- **Matrix Synapse**
  - Secure, decentralized chat platform
  - End-to-end encryption
  - Federation capabilities
  - Requirements:
    * Configuration in `/config/synapse/`
    * Minimum 2GB RAM
    * PostgreSQL database (optional)

## Security Features

### Authentication Layer
- SSO with Authelia
- 2FA support (TOTP)
- Brute-force protection
- Session management
- Access control policies

### Network Security
- SSL/TLS encryption (Auto-renewed Let's Encrypt certificates)
- HTTP security headers
- Rate limiting
- Fail2ban integration
- Network isolation through Docker

### Data Protection
- Encrypted storage
- Regular automated backups
- Secure secret management
- Volume persistence

## Requirements

### Minimum System Requirements
- CPU: 2 cores
- RAM: 4GB minimum (8GB recommended)
- Storage: 40GB minimum (80GB recommended)
- OS: Ubuntu 22.04 LTS or Debian 11
- Domain name with DNS access
- Port 80/443 access

### Software Dependencies
\`\`\`bash
# Core system packages
- docker
- docker-compose
- python3 (3.8+)
- pip3
- git

# Python packages (installed automatically)
- click>=8.0.0
- jinja2>=3.0.0
- pyyaml>=6.0
- psutil>=5.8.0
- requests>=2.26.0
\`\`\`

## Installation Process

### 1. Pre-installation
\`\`\`bash
# Update system
sudo apt update && sudo apt upgrade -y

# Clone repository
git clone https://github.com/yourusername/homelab-setup.git
cd homelab-setup

# Make scripts executable
chmod +x scripts/*.sh
\`\`\`

### 2. Configuration
- Copy `.env.example` to `.env`
- Update domain and other settings
- Review service configurations in `/config`

### 3. Installation
\`\`\`bash
# Run installer
sudo bash scripts/install.sh

# Verify deployment
bash scripts/verify_deployment.sh
\`\`\`

## Service Configuration

### SWAG (Reverse Proxy)
Location: `/config/swag/`
- **SSL Configuration**: Automatic Let's Encrypt certificate management
- **Proxy Configurations**: Service-specific configs in `nginx/proxy-confs/`
- **Security Headers**: Pre-configured security headers

### Authelia
Location: `/config/authelia/`
- **Main Config**: `configuration.yml`
- **Users Database**: `users_database.yml`
- **Access Control**: Rules for service access
- **2FA Setup**: TOTP configuration

### SearXNG
Location: `/config/searxng/`
- **Settings**: `settings.yml`
- **Search Engines**: Customizable sources
- **Privacy Options**: Configurable tracking protection

### Matrix Synapse
Location: `/config/synapse/`
- **Server Config**: `homeserver.yaml`
- **Registration**: Invite-only by default
- **Federation**: Optional server federation
- **Media Storage**: Configurable limits

## Maintenance

### Regular Tasks
1. **Daily**
   - Automated backups
   - Service health checks
   - Log rotation

2. **Weekly**
   - Security updates
   - SSL certificate checks
   - Backup verification

3. **Monthly**
   - Full system updates
   - Performance review
   - Security audit

### Backup System
\`\`\`bash
# Manual backup
bash scripts/backup.sh

# Automated backups (configured in cron)
0 2 * * * /path/to/scripts/backup.sh
\`\`\`

### Updates
\`\`\`bash
# Update all services
bash scripts/update.sh

# Check service status
bash scripts/verify_deployment.sh
\`\`\`

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker logs <service-name>
   
   # Verify configuration
   docker-compose config
   
   # Restart service
   docker-compose restart <service-name>
   ```

2. **Authentication Issues**
   ```bash
   # Check Authelia logs
   docker logs authelia
   
   # Verify Redis connection
   docker logs redis
   ```

3. **SSL Certificate Problems**
   ```bash
   # Check SWAG logs
   docker logs swag
   
   # Force certificate renewal
   docker exec swag /app/force_renew
   ```

### Log Locations
- **Service Logs**: `docker logs <service-name>`
- **SWAG Access Logs**: `/config/swag/log/nginx/`
- **Authelia Logs**: `/config/authelia/`
- **System Logs**: `/var/log/`

### Support Resources
- GitHub Issues
- Documentation
- Community Forums

For detailed service-specific documentation, refer to:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [SWAG_HEIMDALL_GUIDE.md](SWAG_HEIMDALL_GUIDE.md)
- [VPS_HOSTING_GUIDE.md](VPS_HOSTING_GUIDE.md)

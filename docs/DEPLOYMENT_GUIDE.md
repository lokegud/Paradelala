# Deployment Guide - Secure Home-Lab Setup

## Quick Deployment Steps

### Prerequisites
- VPS with Ubuntu 22.04 LTS
- Domain name (optional but recommended)
- SSH access to the server
- Minimum 4GB RAM, 2 CPU cores

### Step 1: Initial Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create non-root user (recommended)
sudo adduser homelab
sudo usermod -aG sudo homelab
sudo su - homelab
```

### Step 2: Clone and Deploy
```bash
# Clone the repository
git clone https://github.com/lokegud/Paradelala.git
cd Paradelala

# Make installer executable
chmod +x scripts/install.sh

# Run the installer
sudo bash scripts/install.sh
```

### Step 3: Follow Interactive Setup
The installer will:
1. **Scan your environment** - Analyze system resources and network
2. **Ask configuration questions** - Domain, services, security preferences
3. **Install dependencies** - Docker, Docker Compose, Python packages
4. **Generate configurations** - Docker Compose, SSL, VPN configs
5. **Deploy services** - Start all selected containers
6. **Configure security** - Firewall, SSH hardening, Fail2ban

### Step 4: Access Your Home-Lab
After deployment:
- **Main dashboard**: `https://your-domain.com`
- **Service URLs**: `https://service.your-domain.com`
- **VPN configs**: Available in `/config/wireguard/`

## Service-Specific Access

### Monitoring Stack
- **Grafana**: `https://grafana.your-domain.com`
  - Default login: admin / (check secrets.json)
- **Prometheus**: `https://prometheus.your-domain.com`

### Applications
- **Portainer**: `https://portainer.your-domain.com`
- **Pi-hole**: `https://pihole.your-domain.com`
- **Nextcloud**: `https://nextcloud.your-domain.com`
- **GitLab**: `https://gitlab.your-domain.com`
- **Vault**: `https://vault.your-domain.com`

### VPN Access
```bash
# Download client configs
scp user@your-server:/path/to/Paradelala/config/wireguard/client1.conf .

# Import to WireGuard client
# Connect and access services via VPN
```

## Post-Deployment Configuration

### 1. Change Default Passwords
```bash
# Check generated passwords
cat secrets.json

# Change passwords in respective services
# Update secrets.json with new passwords
```

### 2. Configure Backup
```bash
# Set up automated backups
./scripts/setup_backup.sh

# Test backup
./scripts/backup.sh
```

### 3. Monitor System Health
- Access Grafana dashboards
- Set up alerting rules
- Configure log retention

### 4. Security Hardening
```bash
# Review security settings
./scripts/security_check.sh

# Update firewall rules if needed
sudo ufw status
```

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker-compose logs -f [service-name]

# Restart services
docker-compose restart [service-name]
```

#### SSL Certificate Issues
```bash
# Check certificate status
docker-compose exec nginx certbot certificates

# Renew certificates manually
docker-compose exec nginx certbot renew

# Check DNS configuration
nslookup your-domain.com
```

#### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Network Connectivity
```bash
# Check open ports
sudo netstat -tlnp

# Test connectivity
curl -I https://your-domain.com

# Check firewall
sudo ufw status verbose
```

### Performance Optimization

#### Resource Monitoring
```bash
# Monitor resource usage
htop
iotop
docker stats

# Check disk usage
df -h
du -sh /var/lib/docker/
```

#### Service Optimization
```bash
# Limit container resources
# Edit docker-compose.yml to add:
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

## Maintenance

### Regular Tasks

#### Weekly
- Check system updates
- Review security logs
- Monitor disk space
- Test backups

#### Monthly
- Update Docker images
- Review access logs
- Check SSL certificate expiry
- Performance review

#### Quarterly
- Security audit
- Backup strategy review
- Capacity planning
- Documentation updates

### Update Procedures

#### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

#### Configuration Updates
```bash
# Pull latest configuration
git pull origin main

# Review changes
git diff HEAD~1

# Apply updates
docker-compose up -d
```

## Backup and Recovery

### Automated Backup
```bash
# Configure backup schedule
crontab -e

# Add backup job (daily at 2 AM)
0 2 * * * /path/to/Paradelala/scripts/backup.sh
```

### Manual Backup
```bash
# Backup all data
./scripts/backup.sh

# Backup specific service
./scripts/backup.sh --service nextcloud
```

### Recovery
```bash
# Restore from backup
./scripts/restore.sh /path/to/backup.tar.gz

# Restore specific service
./scripts/restore.sh --service nextcloud /path/to/backup.tar.gz
```

## Scaling and Expansion

### Adding New Services
1. Edit `docker-compose.yml`
2. Add service configuration
3. Update reverse proxy config
4. Deploy changes: `docker-compose up -d`

### Resource Scaling
```bash
# Vertical scaling (upgrade VPS)
# - Increase RAM/CPU on VPS provider
# - Restart services

# Horizontal scaling (multiple servers)
# - Set up Docker Swarm
# - Configure load balancing
```

## Security Best Practices

### Access Control
- Use SSH keys only
- Implement 2FA where possible
- Regular password rotation
- Principle of least privilege

### Network Security
- VPN-only access for sensitive services
- Regular firewall rule review
- Network segmentation
- DDoS protection

### Data Protection
- Encrypt data at rest
- Secure backup storage
- Regular security audits
- Compliance monitoring

## Support and Community

### Getting Help
- Check documentation first
- Search existing issues
- Join community discussions
- Create detailed bug reports

### Contributing
- Fork the repository
- Create feature branches
- Submit pull requests
- Follow coding standards

---

**Remember**: This setup is designed for personal/development use. For production environments, additional security measures and redundancy should be implemented.

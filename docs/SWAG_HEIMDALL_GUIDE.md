# SWAG and Heimdall Integration Guide

## Overview
This guide covers the integration of SWAG (Secure Web Application Gateway) and Heimdall dashboard into your home-lab setup.

### SWAG Features
- **Automatic SSL certificates** via Let's Encrypt
- **Reverse proxy** with nginx
- **Fail2ban integration** for security
- **Wildcard subdomain support**
- **Built-in security headers**

### Heimdall Features
- **Beautiful dashboard** for service organization
- **Application shortcuts** with custom icons
- **Search functionality** across services
- **Responsive design** for mobile access
- **Easy configuration** via web interface

## Configuration

### SWAG Setup
When you enable SWAG during installation, it will:

1. **Replace nginx** as the primary reverse proxy
2. **Generate SSL certificates** automatically for your domain
3. **Configure subdomain routing** for all services
4. **Set up security policies** and headers
5. **Enable fail2ban** protection

### Heimdall Setup
Heimdall serves as your main dashboard and will be accessible at:
- **Main domain**: `https://yourdomain.com`
- **Direct access**: `https://heimdall.yourdomain.com`

## Service URLs with SWAG

### Core Services
- **Heimdall Dashboard**: `https://yourdomain.com`
- **Portainer**: `https://portainer.yourdomain.com`
- **Grafana**: `https://grafana.yourdomain.com`
- **Prometheus**: `https://prometheus.yourdomain.com`

### Optional Services
- **Pi-hole**: `https://pihole.yourdomain.com`
- **Nextcloud**: `https://nextcloud.yourdomain.com`
- **GitLab**: `https://gitlab.yourdomain.com`
- **Vault**: `https://vault.yourdomain.com`

## SWAG Configuration Files

### Main Configuration
```bash
# Location: ./config/swag/nginx/nginx.conf
# Main nginx configuration with security headers
```

### Subdomain Configurations
```bash
# Location: ./config/swag/nginx/proxy-confs/
# Individual service configurations:
# - heimdall.subdomain.conf
# - portainer.subdomain.conf
# - grafana.subdomain.conf
# - etc.
```

### SSL Certificates
```bash
# Location: ./config/swag/etc/letsencrypt/live/yourdomain.com/
# Automatic certificate management
```

## Heimdall Configuration

### Initial Setup
1. **Access Heimdall** at `https://yourdomain.com`
2. **Add applications** using the "+" button
3. **Configure app details**:
   - Name: Service name
   - URL: Service URL (e.g., https://portainer.yourdomain.com)
   - Icon: Choose from built-in icons or upload custom
   - Color: Set theme color

### Application Examples

#### Portainer
- **Name**: Portainer
- **URL**: https://portainer.yourdomain.com
- **Icon**: portainer.png
- **Description**: Container Management

#### Grafana
- **Name**: Grafana
- **URL**: https://grafana.yourdomain.com
- **Icon**: grafana.png
- **Description**: Monitoring Dashboard

#### Pi-hole
- **Name**: Pi-hole
- **URL**: https://pihole.yourdomain.com
- **Icon**: pihole.png
- **Description**: Network Ad Blocker

## Security Considerations

### SWAG Security Features
- **Automatic SSL/TLS** with strong ciphers
- **Security headers** (HSTS, CSP, etc.)
- **Fail2ban integration** for brute force protection
- **Rate limiting** on sensitive endpoints
- **IP whitelisting** capabilities

### Recommended Security Settings
```nginx
# Custom security headers in SWAG
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## Troubleshooting

### Common SWAG Issues

#### Certificate Generation Failed
```bash
# Check SWAG logs
docker-compose logs swag

# Verify domain DNS
nslookup yourdomain.com

# Check port 80/443 accessibility
curl -I http://yourdomain.com
```

#### Subdomain Not Working
```bash
# Check subdomain configuration
ls -la config/swag/nginx/proxy-confs/

# Verify service is running
docker-compose ps

# Check nginx configuration
docker-compose exec swag nginx -t
```

### Common Heimdall Issues

#### Dashboard Not Loading
```bash
# Check Heimdall logs
docker-compose logs heimdall

# Verify container is running
docker-compose ps heimdall

# Check port accessibility
curl -I http://localhost:8080
```

#### Applications Not Accessible
- **Verify URLs** are correct in Heimdall settings
- **Check service status** in Portainer or docker-compose
- **Confirm SSL certificates** are valid

## Customization

### Custom Heimdall Themes
1. **Access settings** in Heimdall
2. **Choose theme** from available options
3. **Customize colors** and layout
4. **Upload custom background** if desired

### Custom SWAG Configurations
```bash
# Add custom nginx configurations
# Location: ./config/swag/nginx/site-confs/default
```

### Adding New Services
1. **Add service** to docker-compose.yml
2. **Create subdomain config** in SWAG
3. **Add application** to Heimdall dashboard
4. **Test accessibility** and SSL

## Backup and Restore

### SWAG Backup
```bash
# Backup SWAG configuration
tar -czf swag-backup.tar.gz ./config/swag/

# Backup certificates
tar -czf certs-backup.tar.gz ./config/swag/etc/letsencrypt/
```

### Heimdall Backup
```bash
# Backup Heimdall configuration
tar -czf heimdall-backup.tar.gz ./config/heimdall/
```

### Restore Process
```bash
# Stop services
docker-compose down

# Restore configurations
tar -xzf swag-backup.tar.gz
tar -xzf heimdall-backup.tar.gz

# Start services
docker-compose up -d
```

## Performance Optimization

### SWAG Optimization
- **Enable gzip compression** for faster loading
- **Configure caching** for static assets
- **Optimize SSL settings** for performance
- **Use HTTP/2** for improved speed

### Heimdall Optimization
- **Optimize images** for faster loading
- **Use CDN** for external resources
- **Enable caching** in browser
- **Minimize applications** on main page

## Monitoring

### SWAG Monitoring
- **Access logs**: `./config/swag/log/nginx/access.log`
- **Error logs**: `./config/swag/log/nginx/error.log`
- **Fail2ban logs**: `./config/swag/log/fail2ban/`

### Heimdall Monitoring
- **Application status** via dashboard
- **Response times** for services
- **SSL certificate expiry** warnings

---

**Note**: SWAG and Heimdall provide a professional-grade reverse proxy and dashboard solution for your home-lab, offering both security and usability improvements over basic nginx setups.

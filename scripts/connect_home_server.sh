#!/bin/bash
# Home Server Connection Script
# This script helps connect your home server to the VPS-hosted home-lab

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log "ERROR" "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Display banner
show_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    Home Server Connection Setup"
    echo "    Secure Home-Lab Bridge Configuration"
    echo "=================================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if we're on the VPS or home server
    read -p "Are you running this on your VPS (v) or Home Server (h)? [v/h]: " location
    
    case $location in
        v|V)
            LOCATION="vps"
            log "INFO" "Configuring VPS side of the connection"
            ;;
        h|H)
            LOCATION="home"
            log "INFO" "Configuring home server side of the connection"
            ;;
        *)
            log "ERROR" "Invalid selection. Please choose 'v' for VPS or 'h' for home server"
            exit 1
            ;;
    esac
    
    # Check for required tools
    local required_tools=("curl" "ssh" "nc")
    for tool in "${required_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log "ERROR" "$tool is required but not installed"
            exit 1
        fi
    done
    
    log "SUCCESS" "Prerequisites check completed"
}

# Get connection details
get_connection_details() {
    log "INFO" "Gathering connection details..."
    
    if [[ $LOCATION == "vps" ]]; then
        # VPS configuration
        read -p "Enter your home server's public IP (or dynamic DNS): " HOME_SERVER_IP
        read -p "Enter SSH port for home server [22]: " HOME_SSH_PORT
        HOME_SSH_PORT=${HOME_SSH_PORT:-22}
        read -p "Enter username for home server: " HOME_USER
        read -p "Enter the service port you want to expose [8080]: " HOME_SERVICE_PORT
        HOME_SERVICE_PORT=${HOME_SERVICE_PORT:-8080}
        read -p "Enter subdomain for this service (e.g., homeserver): " SUBDOMAIN
        
    else
        # Home server configuration
        read -p "Enter your VPS IP address: " VPS_IP
        read -p "Enter VPS SSH port [22]: " VPS_SSH_PORT
        VPS_SSH_PORT=${VPS_SSH_PORT:-22}
        read -p "Enter VPS username: " VPS_USER
        read -p "Enter local service IP [127.0.0.1]: " LOCAL_IP
        LOCAL_IP=${LOCAL_IP:-127.0.0.1}
        read -p "Enter local service port [8080]: " LOCAL_PORT
        LOCAL_PORT=${LOCAL_PORT:-8080}
    fi
}

# Test connectivity
test_connectivity() {
    log "INFO" "Testing connectivity..."
    
    if [[ $LOCATION == "vps" ]]; then
        # Test connection to home server
        log "INFO" "Testing SSH connection to home server..."
        if ssh -o ConnectTimeout=10 -o BatchMode=yes -p $HOME_SSH_PORT $HOME_USER@$HOME_SERVER_IP exit 2>/dev/null; then
            log "SUCCESS" "SSH connection to home server successful"
        else
            log "WARNING" "SSH connection failed. Please ensure:"
            echo "  - Home server is accessible from internet"
            echo "  - SSH keys are properly configured"
            echo "  - Firewall allows SSH on port $HOME_SSH_PORT"
        fi
        
        # Test service port
        log "INFO" "Testing service port connectivity..."
        if nc -z -w5 $HOME_SERVER_IP $HOME_SERVICE_PORT 2>/dev/null; then
            log "SUCCESS" "Service port $HOME_SERVICE_PORT is accessible"
        else
            log "WARNING" "Service port $HOME_SERVICE_PORT is not accessible"
            echo "  - Ensure the service is running on your home server"
            echo "  - Check firewall rules on home server"
            echo "  - Verify port forwarding on your router"
        fi
        
    else
        # Test connection to VPS
        log "INFO" "Testing SSH connection to VPS..."
        if ssh -o ConnectTimeout=10 -o BatchMode=yes -p $VPS_SSH_PORT $VPS_USER@$VPS_IP exit 2>/dev/null; then
            log "SUCCESS" "SSH connection to VPS successful"
        else
            log "ERROR" "SSH connection to VPS failed"
            exit 1
        fi
        
        # Test local service
        log "INFO" "Testing local service..."
        if nc -z -w5 $LOCAL_IP $LOCAL_PORT 2>/dev/null; then
            log "SUCCESS" "Local service is running on $LOCAL_IP:$LOCAL_PORT"
        else
            log "WARNING" "Local service is not accessible on $LOCAL_IP:$LOCAL_PORT"
            echo "  - Ensure your service is running"
            echo "  - Check if the service binds to the correct interface"
        fi
    fi
}

# Configure SSH tunnel
configure_ssh_tunnel() {
    log "INFO" "Configuring SSH tunnel..."
    
    if [[ $LOCATION == "vps" ]]; then
        # VPS side - configure reverse proxy
        log "INFO" "Setting up reverse proxy configuration..."
        
        # Create nginx configuration for the home service
        cat > "/tmp/${SUBDOMAIN}.conf" << EOF
server {
    listen 80;
    server_name ${SUBDOMAIN}.${DOMAIN:-localhost};
    
    location / {
        proxy_pass http://127.0.0.1:${HOME_SERVICE_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
        
        log "SUCCESS" "Nginx configuration created for ${SUBDOMAIN}"
        echo "Copy /tmp/${SUBDOMAIN}.conf to your nginx sites-enabled directory"
        
    else
        # Home server side - create SSH tunnel
        log "INFO" "Creating SSH tunnel configuration..."
        
        # Create systemd service for persistent tunnel
        cat > "/tmp/homelab-tunnel.service" << EOF
[Unit]
Description=Home-Lab SSH Tunnel
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/ssh -N -R ${LOCAL_PORT}:${LOCAL_IP}:${LOCAL_PORT} -o ServerAliveInterval=60 -o ExitOnForwardFailure=yes -p ${VPS_SSH_PORT} ${VPS_USER}@${VPS_IP}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        log "SUCCESS" "Systemd service created"
        echo "To install the service:"
        echo "  sudo cp /tmp/homelab-tunnel.service /etc/systemd/system/"
        echo "  sudo systemctl enable homelab-tunnel"
        echo "  sudo systemctl start homelab-tunnel"
    fi
}

# Configure WireGuard (alternative to SSH tunnel)
configure_wireguard() {
    log "INFO" "Setting up WireGuard configuration..."
    
    if [[ $LOCATION == "vps" ]]; then
        # VPS side - add home server as WireGuard peer
        log "INFO" "Adding home server as WireGuard peer..."
        
        # Generate keys for home server
        HOME_PRIVATE_KEY=$(wg genkey)
        HOME_PUBLIC_KEY=$(echo $HOME_PRIVATE_KEY | wg pubkey)
        
        echo "Home server WireGuard configuration:"
        cat << EOF
[Interface]
PrivateKey = $HOME_PRIVATE_KEY
Address = 10.0.0.100/24
DNS = 10.0.0.1

[Peer]
PublicKey = $(sudo cat /etc/wireguard/server_public.key 2>/dev/null || echo "VPS_PUBLIC_KEY_HERE")
Endpoint = $(curl -s ifconfig.me):51820
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
EOF
        
        echo ""
        echo "Add this peer to your VPS WireGuard configuration:"
        echo "[Peer]"
        echo "PublicKey = $HOME_PUBLIC_KEY"
        echo "AllowedIPs = 10.0.0.100/32"
        
    else
        # Home server side - create WireGuard config
        log "INFO" "Creating WireGuard client configuration..."
        
        read -p "Enter VPS WireGuard public key: " VPS_PUBLIC_KEY
        read -p "Enter your assigned IP (e.g., 10.0.0.100): " WG_IP
        
        PRIVATE_KEY=$(wg genkey)
        PUBLIC_KEY=$(echo $PRIVATE_KEY | wg pubkey)
        
        cat > "/tmp/homelab.conf" << EOF
[Interface]
PrivateKey = $PRIVATE_KEY
Address = $WG_IP/24
DNS = 10.0.0.1

[Peer]
PublicKey = $VPS_PUBLIC_KEY
Endpoint = $VPS_IP:51820
AllowedIPs = 10.0.0.0/24
PersistentKeepalive = 25
EOF
        
        log "SUCCESS" "WireGuard configuration created at /tmp/homelab.conf"
        echo "Your public key (share with VPS admin): $PUBLIC_KEY"
        echo ""
        echo "To activate:"
        echo "  sudo cp /tmp/homelab.conf /etc/wireguard/"
        echo "  sudo systemctl enable wg-quick@homelab"
        echo "  sudo systemctl start wg-quick@homelab"
    fi
}

# Setup monitoring
setup_monitoring() {
    log "INFO" "Setting up connection monitoring..."
    
    if [[ $LOCATION == "home" ]]; then
        # Create monitoring script
        cat > "/tmp/tunnel-monitor.sh" << 'EOF'
#!/bin/bash
# Monitor tunnel connectivity

VPS_IP="VPS_IP_PLACEHOLDER"
LOCAL_PORT="LOCAL_PORT_PLACEHOLDER"

check_tunnel() {
    if pgrep -f "ssh.*$VPS_IP" > /dev/null; then
        echo "$(date): Tunnel is active"
        return 0
    else
        echo "$(date): Tunnel is down, attempting restart"
        systemctl restart homelab-tunnel
        return 1
    fi
}

check_service() {
    if nc -z 127.0.0.1 $LOCAL_PORT; then
        echo "$(date): Local service is responding"
        return 0
    else
        echo "$(date): Local service is not responding"
        return 1
    fi
}

# Main monitoring loop
check_tunnel
check_service
EOF
        
        # Replace placeholders
        sed -i "s/VPS_IP_PLACEHOLDER/$VPS_IP/g" /tmp/tunnel-monitor.sh
        sed -i "s/LOCAL_PORT_PLACEHOLDER/$LOCAL_PORT/g" /tmp/tunnel-monitor.sh
        
        chmod +x /tmp/tunnel-monitor.sh
        
        log "SUCCESS" "Monitoring script created at /tmp/tunnel-monitor.sh"
        echo "Add to crontab for regular monitoring:"
        echo "  */5 * * * * /path/to/tunnel-monitor.sh >> /var/log/tunnel-monitor.log"
    fi
}

# Generate documentation
generate_docs() {
    log "INFO" "Generating connection documentation..."
    
    cat > "/tmp/home-server-connection.md" << EOF
# Home Server Connection Documentation

## Configuration Summary
- **Location**: $LOCATION
- **Date**: $(date)

EOF
    
    if [[ $LOCATION == "vps" ]]; then
        cat >> "/tmp/home-server-connection.md" << EOF
### VPS Configuration
- **Home Server IP**: $HOME_SERVER_IP
- **Home SSH Port**: $HOME_SSH_PORT
- **Home User**: $HOME_USER
- **Service Port**: $HOME_SERVICE_PORT
- **Subdomain**: $SUBDOMAIN

### Access URL
- **Service URL**: https://${SUBDOMAIN}.${DOMAIN:-your-domain.com}

### Nginx Configuration
Location: /etc/nginx/sites-enabled/${SUBDOMAIN}.conf

### SSL Certificate
Run: \`certbot --nginx -d ${SUBDOMAIN}.${DOMAIN:-your-domain.com}\`
EOF
    else
        cat >> "/tmp/home-server-connection.md" << EOF
### Home Server Configuration
- **VPS IP**: $VPS_IP
- **VPS SSH Port**: $VPS_SSH_PORT
- **VPS User**: $VPS_USER
- **Local Service**: $LOCAL_IP:$LOCAL_PORT

### SSH Tunnel Command
\`\`\`bash
ssh -N -R $LOCAL_PORT:$LOCAL_IP:$LOCAL_PORT -p $VPS_SSH_PORT $VPS_USER@$VPS_IP
\`\`\`

### Systemd Service
Location: /etc/systemd/system/homelab-tunnel.service

### Monitoring
- Check tunnel: \`pgrep -f "ssh.*$VPS_IP"\`
- Check service: \`nc -z $LOCAL_IP $LOCAL_PORT\`
EOF
    fi
    
    cat >> "/tmp/home-server-connection.md" << EOF

## Troubleshooting

### Common Issues
1. **Connection refused**: Check firewall rules
2. **Authentication failed**: Verify SSH keys
3. **Service unreachable**: Confirm service is running
4. **DNS issues**: Check domain configuration

### Useful Commands
\`\`\`bash
# Check SSH connection
ssh -v user@server

# Test port connectivity
nc -zv host port

# Monitor tunnel
journalctl -u homelab-tunnel -f

# Check nginx logs
tail -f /var/log/nginx/error.log
\`\`\`

## Security Notes
- Use SSH keys instead of passwords
- Regularly update both servers
- Monitor access logs
- Use fail2ban for protection
- Consider VPN instead of direct exposure
EOF
    
    log "SUCCESS" "Documentation generated at /tmp/home-server-connection.md"
}

# Main execution
main() {
    show_banner
    check_root
    check_prerequisites
    get_connection_details
    test_connectivity
    
    echo ""
    log "INFO" "Choose connection method:"
    echo "1) SSH Tunnel (recommended for simple setups)"
    echo "2) WireGuard VPN (recommended for security)"
    echo "3) Both (maximum flexibility)"
    read -p "Enter your choice [1-3]: " method
    
    case $method in
        1)
            configure_ssh_tunnel
            ;;
        2)
            configure_wireguard
            ;;
        3)
            configure_ssh_tunnel
            configure_wireguard
            ;;
        *)
            log "ERROR" "Invalid choice"
            exit 1
            ;;
    esac
    
    setup_monitoring
    generate_docs
    
    echo ""
    log "SUCCESS" "Home server connection setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Review generated configurations in /tmp/"
    echo "2. Copy configurations to appropriate locations"
    echo "3. Test the connection"
    echo "4. Set up monitoring"
    echo ""
    echo "Documentation: /tmp/home-server-connection.md"
}

# Run main function
main "$@"

#!/bin/bash
# Home Server Connection Script
# This script helps users connect their VPS home-lab to their home server

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

# Install required packages
install_dependencies() {
    log "INFO" "Installing required dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install required packages
    sudo apt install -y openssh-client autossh nginx-light socat netcat-openbsd
    
    log "SUCCESS" "Dependencies installed"
}

# Generate SSH key pair for secure connection
generate_ssh_keys() {
    local key_path="$HOME/.ssh/homelab_tunnel"
    
    if [[ -f "$key_path" ]]; then
        log "INFO" "SSH key already exists at $key_path"
        return 0
    fi
    
    log "INFO" "Generating SSH key pair for secure tunnel..."
    ssh-keygen -t ed25519 -f "$key_path" -N "" -C "homelab-tunnel-$(date +%Y%m%d)"
    
    log "SUCCESS" "SSH key generated at $key_path"
    log "INFO" "Public key content:"
    echo "----------------------------------------"
    cat "$key_path.pub"
    echo "----------------------------------------"
    log "WARNING" "Copy the above public key to your home server's ~/.ssh/authorized_keys"
}

# Configure reverse SSH tunnel
setup_reverse_tunnel() {
    local home_server_ip=""
    local home_server_port=""
    local home_server_user=""
    local local_port=""
    local remote_port=""
    
    echo
    log "INFO" "Setting up reverse SSH tunnel to home server"
    echo
    
    # Get home server details
    read -p "Enter your home server IP address: " home_server_ip
    read -p "Enter SSH port on home server (default 22): " home_server_port
    home_server_port=${home_server_port:-22}
    read -p "Enter username on home server: " home_server_user
    read -p "Enter port to expose on home server (default 8080): " local_port
    local_port=${local_port:-8080}
    read -p "Enter remote port to forward to (default 80): " remote_port
    remote_port=${remote_port:-80}
    
    # Create tunnel configuration
    local config_file="$HOME/.ssh/homelab_tunnel_config"
    cat > "$config_file" << EOF
# Home Server Tunnel Configuration
HOME_SERVER_IP="$home_server_ip"
HOME_SERVER_PORT="$home_server_port"
HOME_SERVER_USER="$home_server_user"
LOCAL_PORT="$local_port"
REMOTE_PORT="$remote_port"
SSH_KEY="$HOME/.ssh/homelab_tunnel"
EOF
    
    # Create tunnel script
    local tunnel_script="$HOME/bin/start_tunnel.sh"
    mkdir -p "$HOME/bin"
    
    cat > "$tunnel_script" << 'EOF'
#!/bin/bash
# Load configuration
source "$HOME/.ssh/homelab_tunnel_config"

# Start reverse SSH tunnel
autossh -M 0 \
    -o "ServerAliveInterval 30" \
    -o "ServerAliveCountMax 3" \
    -o "StrictHostKeyChecking=no" \
    -o "ExitOnForwardFailure=yes" \
    -i "$SSH_KEY" \
    -R "$LOCAL_PORT:localhost:$REMOTE_PORT" \
    -N "$HOME_SERVER_USER@$HOME_SERVER_IP" \
    -p "$HOME_SERVER_PORT"
EOF
    
    chmod +x "$tunnel_script"
    
    log "SUCCESS" "Tunnel configuration created"
    log "INFO" "Configuration saved to: $config_file"
    log "INFO" "Tunnel script created at: $tunnel_script"
}

# Create systemd service for persistent tunnel
create_tunnel_service() {
    log "INFO" "Creating systemd service for persistent tunnel..."
    
    local service_file="/tmp/homelab-tunnel.service"
    cat > "$service_file" << EOF
[Unit]
Description=Home Lab Reverse SSH Tunnel
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$HOME/bin/start_tunnel.sh
Restart=always
RestartSec=10
Environment=AUTOSSH_GATETIME=0

[Install]
WantedBy=multi-user.target
EOF
    
    # Install service
    sudo mv "$service_file" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    sudo systemctl enable homelab-tunnel.service
    
    log "SUCCESS" "Systemd service created and enabled"
    log "INFO" "Use 'sudo systemctl start homelab-tunnel' to start the tunnel"
    log "INFO" "Use 'sudo systemctl status homelab-tunnel' to check status"
}

# Configure nginx proxy for home server
setup_nginx_proxy() {
    log "INFO" "Setting up nginx proxy for home server access..."
    
    read -p "Enter subdomain for home server (e.g., 'home' for home.yourdomain.com): " subdomain
    read -p "Enter your domain name: " domain
    
    local nginx_config="/etc/nginx/sites-available/homeserver-proxy"
    
    sudo tee "$nginx_config" > /dev/null << EOF
server {
    listen 80;
    server_name $subdomain.$domain;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
    
    # Enable site
    sudo ln -sf "$nginx_config" "/etc/nginx/sites-enabled/"
    sudo nginx -t && sudo systemctl reload nginx
    
    log "SUCCESS" "Nginx proxy configured for $subdomain.$domain"
    log "INFO" "Your home server will be accessible at: http://$subdomain.$domain"
}

# Test connection to home server
test_connection() {
    log "INFO" "Testing connection to home server..."
    
    # Load configuration
    if [[ -f "$HOME/.ssh/homelab_tunnel_config" ]]; then
        source "$HOME/.ssh/homelab_tunnel_config"
    else
        log "ERROR" "Tunnel configuration not found. Run setup first."
        return 1
    fi
    
    # Test SSH connection
    log "INFO" "Testing SSH connection..."
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
           "$HOME_SERVER_USER@$HOME_SERVER_IP" -p "$HOME_SERVER_PORT" "echo 'SSH connection successful'"; then
        log "SUCCESS" "SSH connection to home server successful"
    else
        log "ERROR" "SSH connection failed. Check your configuration and network."
        return 1
    fi
    
    # Test tunnel
    log "INFO" "Testing reverse tunnel..."
    if nc -z localhost "$LOCAL_PORT" 2>/dev/null; then
        log "SUCCESS" "Tunnel is active and port $LOCAL_PORT is accessible"
    else
        log "WARNING" "Tunnel port $LOCAL_PORT is not accessible. Start the tunnel service."
    fi
}

# Monitor tunnel status
monitor_tunnel() {
    log "INFO" "Monitoring tunnel status..."
    
    while true; do
        clear
        echo "=== Home Server Tunnel Monitor ==="
        echo "Press Ctrl+C to exit"
        echo
        
        # Service status
        if systemctl is-active --quiet homelab-tunnel; then
            log "SUCCESS" "Tunnel service is running"
        else
            log "ERROR" "Tunnel service is not running"
        fi
        
        # Port status
        if nc -z localhost 8080 2>/dev/null; then
            log "SUCCESS" "Local port 8080 is accessible"
        else
            log "WARNING" "Local port 8080 is not accessible"
        fi
        
        # Connection test
        if [[ -f "$HOME/.ssh/homelab_tunnel_config" ]]; then
            source "$HOME/.ssh/homelab_tunnel_config"
            if timeout 5 ssh -i "$SSH_KEY" -o ConnectTimeout=5 \
                   "$HOME_SERVER_USER@$HOME_SERVER_IP" -p "$HOME_SERVER_PORT" "exit" 2>/dev/null; then
                log "SUCCESS" "Home server is reachable"
            else
                log "ERROR" "Home server is not reachable"
            fi
        fi
        
        echo
        echo "Last updated: $(date)"
        sleep 10
    done
}

# Main menu
show_menu() {
    echo
    echo "=== Home Server Connection Setup ==="
    echo "1. Install dependencies"
    echo "2. Generate SSH keys"
    echo "3. Setup reverse tunnel"
    echo "4. Create systemd service"
    echo "5. Setup nginx proxy"
    echo "6. Test connection"
    echo "7. Monitor tunnel"
    echo "8. Exit"
    echo
}

# Main function
main() {
    check_root
    
    while true; do
        show_menu
        read -p "Choose an option (1-8): " choice
        
        case $choice in
            1)
                install_dependencies
                ;;
            2)
                generate_ssh_keys
                ;;
            3)
                setup_reverse_tunnel
                ;;
            4)
                create_tunnel_service
                ;;
            5)
                setup_nginx_proxy
                ;;
            6)
                test_connection
                ;;
            7)
                monitor_tunnel
                ;;
            8)
                log "INFO" "Exiting..."
                exit 0
                ;;
            *)
                log "ERROR" "Invalid option. Please choose 1-8."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"

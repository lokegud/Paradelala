#!/bin/bash
#
# Secure Home-Lab Setup Installer
# This script installs dependencies and runs the orchestrator
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                  Secure Home-Lab Setup v1.0                   ║"
    echo "║                                                               ║"
    echo "║  AI-Powered Infrastructure Deployment for Your Home Lab       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root or with sudo"
        exit 1
    fi
}

check_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot determine OS. This script requires Ubuntu 20.04+ or Debian 11+"
        exit 1
    fi
    
    if [[ "$OS" != "ubuntu" && "$OS" != "debian" ]]; then
        print_warning "This script is designed for Ubuntu/Debian. Your OS: $OS"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

install_system_packages() {
    print_info "Installing system packages..."
    
    # Update package list
    apt-get update -qq
    
    # Install required packages
    PACKAGES=(
        python3
        python3-pip
        python3-venv
        git
        curl
        wget
        net-tools
        dnsutils
        nmap
        jq
        htop
        iotop
        ncdu
        tmux
        vim
        ufw
        fail2ban
        unattended-upgrades
        apt-transport-https
        ca-certificates
        gnupg
        lsb-release
        software-properties-common
    )
    
    for package in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            print_info "Installing $package..."
            apt-get install -y -qq "$package" > /dev/null 2>&1
        fi
    done
    
    print_success "System packages installed"
}

install_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is already installed"
        return
    fi
    
    print_info "Installing Docker..."
    
    # Remove old versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    if [[ -n "$SUDO_USER" ]]; then
        usermod -aG docker "$SUDO_USER"
    fi
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "Docker installed successfully"
}

install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is already installed"
        return
    fi
    
    print_info "Installing Docker Compose..."
    
    # Install Docker Compose V2
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed successfully"
}

setup_python_environment() {
    print_info "Setting up Python environment..."
    
    # Get the actual user (not root if using sudo)
    if [[ -n "$SUDO_USER" ]]; then
        ACTUAL_USER=$SUDO_USER
        USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    else
        ACTUAL_USER=$USER
        USER_HOME=$HOME
    fi
    
    # Create virtual environment
    VENV_PATH="$USER_HOME/.homelab-venv"
    
    if [[ ! -d "$VENV_PATH" ]]; then
        sudo -u "$ACTUAL_USER" python3 -m venv "$VENV_PATH"
    fi
    
# Install Python packages
print_info "Installing Python dependencies..."

# Create requirements file
cat > /tmp/requirements.txt << EOF
click>=8.0.0
jinja2>=3.0.0
pyyaml>=6.0
psutil>=5.8.0
py-cpuinfo>=8.0.0
requests>=2.26.0
netifaces>=0.11.0
python-nmap>=0.7.1
distro>=1.6.0
EOF

# Install packages in virtual environment
sudo -u "$ACTUAL_USER" "$VENV_PATH/bin/pip" install --upgrade pip
sudo -u "$ACTUAL_USER" "$VENV_PATH/bin/pip" install -r /tmp/requirements.txt
}

configure_firewall() {
    print_info "Configuring basic firewall rules..."
    
    # Enable UFW
    ufw --force enable
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (check current SSH port)
    SSH_PORT=$(grep "^Port" /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}')
    if [[ -z "$SSH_PORT" ]]; then
        SSH_PORT="22"
    fi
    ufw allow "$SSH_PORT/tcp" comment "SSH"
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"
    
    print_success "Firewall configured"
}

run_orchestrator() {
    print_info "Starting Home Lab setup orchestrator..."
    
    # Get the actual user
    if [[ -n "$SUDO_USER" ]]; then
        ACTUAL_USER=$SUDO_USER
        USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    else
        ACTUAL_USER=$USER
        USER_HOME=$HOME
    fi
    
    VENV_PATH="$USER_HOME/.homelab-venv"
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    # Run the orchestrator
    cd "$PROJECT_ROOT"
    sudo -u "$ACTUAL_USER" "$VENV_PATH/bin/python" src/orchestrator.py "$@"
}

cleanup() {
    print_info "Cleaning up temporary files..."
    rm -f /tmp/requirements.txt
    print_success "Cleanup complete"
}

# Main execution
install_nodejs() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | sed 's/v//')
        NODE_MAJOR_VERSION=$(echo "$NODE_VERSION" | cut -d. -f1)
        if [ "$NODE_MAJOR_VERSION" -ge 20 ]; then
            print_success "Node.js version $NODE_VERSION is already installed"
            return
        else
            print_warning "Node.js version $NODE_VERSION is installed but version 20 or higher is required"
        fi
    else
        print_info "Node.js is not installed"
    fi

    print_info "Installing Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs

    NODE_VERSION_INSTALLED=$(node -v | sed 's/v//')
    if [ "$(echo $NODE_VERSION_INSTALLED | cut -d. -f1)" -ge 20 ]; then
        print_success "Node.js version $NODE_VERSION_INSTALLED installed successfully"
    else
        print_error "Failed to install Node.js 20.x"
        exit 1
    fi
}

install_gcli() {
    print_info "Installing Gemini CLI (gcli) from source..."

    # Change to gcli directory
    cd "$(dirname "$0")/../gcli"

    # Install dependencies
    npm ci

    # Build the project
    npm run build

    # Link the CLI globally
    npm link

    print_success "Gemini CLI installed successfully"
}

main() {
    print_banner
    
    # Check prerequisites
    check_root
    check_os
    
    echo
    print_info "This script will install and configure your secure home lab."
    print_info "It will install: Docker, Docker Compose, Python packages, and security tools."
    echo
    read -p "Continue with installation? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    echo
    
    # Installation steps
    install_system_packages
    install_nodejs
    install_docker
    install_docker_compose
    setup_python_environment
    configure_firewall
    install_gcli
    
    echo
    print_success "All dependencies installed successfully!"
    echo
    
    # Run the orchestrator
    run_orchestrator "$@"
    
    # Cleanup
    cleanup
    
    echo
    print_success "Installation complete!"
    
    # Final instructions
    if [[ -n "$SUDO_USER" ]]; then
        echo
        print_warning "You've been added to the docker group."
        print_warning "Please log out and back in for this to take effect."
        print_warning "Or run: newgrp docker"
    fi
}

# Run main function with all arguments
main "$@"

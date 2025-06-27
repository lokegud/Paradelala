#!/bin/bash
# Homelab Builder Installation Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║        🏠 HOMELAB BUILDER v1.0.0          ║"
echo "║   Intelligent Homelab Installation Tool   ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root!"
   print_info "Please run as a regular user with sudo privileges."
   exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system packages
install_system_packages() {
    print_info "Installing system dependencies..."
    
    # Detect OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS. Please install dependencies manually."
        exit 1
    fi
    
    # Install packages based on OS
    case $OS in
        ubuntu|debian)
            print_info "Detected Debian/Ubuntu system"
            sudo apt-get update
            sudo apt-get install -y \
                python3 python3-pip python3-venv \
                docker.io docker-compose \
                git curl wget \
                wireguard-tools \
                ufw fail2ban
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            ;;
            
        fedora|centos|rhel)
            print_info "Detected RHEL-based system"
            sudo dnf install -y \
                python3 python3-pip \
                docker docker-compose \
                git curl wget \
                wireguard-tools \
                firewalld fail2ban
            
            # Start Docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            ;;
            
        arch|manjaro)
            print_info "Detected Arch-based system"
            sudo pacman -Sy --noconfirm \
                python python-pip \
                docker docker-compose \
                git curl wget \
                wireguard-tools \
                ufw fail2ban
            
            # Start Docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            ;;
            
        *)
            print_error "Unsupported OS: $OS"
            print_info "Please install the following manually:"
            print_info "- Python 3.8+"
            print_info "- Docker and Docker Compose"
            print_info "- Git"
            print_info "- WireGuard tools (optional)"
            exit 1
            ;;
    esac
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if [[ $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc) -eq 1 ]]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python $PYTHON_VERSION is too old. Python 3.8+ required."
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check Docker
check_docker() {
    print_info "Checking Docker installation..."
    
    if command_exists docker; then
        print_success "Docker found"
        
        # Check if Docker daemon is running
        if ! sudo docker info >/dev/null 2>&1; then
            print_warning "Docker daemon is not running. Starting Docker..."
            sudo systemctl start docker
        fi
    else
        print_error "Docker not found"
        return 1
    fi
    
    if command_exists docker-compose; then
        print_success "Docker Compose found"
    else
        print_error "Docker Compose not found"
        return 1
    fi
    
    return 0
}

# Main installation
main() {
    print_info "Starting Homelab Builder installation..."
    
    # Check prerequisites
    INSTALL_DEPS=false
    
    if ! check_docker; then
        INSTALL_DEPS=true
    fi
    
    check_python
    
    # Ask to install dependencies
    if [[ "$INSTALL_DEPS" == "true" ]]; then
        echo
        read -p "Would you like to install missing dependencies? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_system_packages
            print_warning "Please log out and back in for Docker group changes to take effect"
            print_info "Then run this script again"
            exit 0
        else
            print_error "Cannot proceed without required dependencies"
            exit 1
        fi
    fi
    
    # Create virtual environment
    print_info "Creating Python virtual environment..."
    if [[ -d "venv" ]]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip wheel setuptools
    
    # Install Python requirements
    print_info "Installing Python requirements..."
    pip install -r requirements.txt
    
    # Create necessary directories
    print_info "Creating directory structure..."
    sudo mkdir -p /opt/homelab/{configs,data,logs,backups,certs}
    sudo chown -R $USER:$USER /opt/homelab
    
    # Make scripts executable
    chmod +x installer/main.py
    
    print_success "Installation complete!"
    echo
    print_info "Starting Homelab Builder..."
    echo
    
    # Run the main installer
    python installer/main.py
}

# Run main function
main

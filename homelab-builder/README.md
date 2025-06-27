# 🏠 Homelab Builder

An intelligent, interactive installer for creating secure and private home-labs that can be deployed to a VPS and used as a proxy to your home server.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-beta-yellow.svg)

## 🚀 Features

- **Intelligent Environment Scanning**: Automatically detects system resources, network configuration, and installed software
- **Interactive Survey**: Asks targeted questions to understand your specific needs and use cases
- **AI-Powered Recommendations**: Suggests the best services based on your requirements and available resources
- **Automated Deployment**: Sets up all services with Docker Compose in a single command
- **Secure Tunneling**: Multiple options including WireGuard VPN, Cloudflare Tunnel, and reverse proxy
- **Service Catalog**: Pre-configured templates for popular homelab services:
  - Media servers (Jellyfin, Plex)
  - Development tools (GitLab, Gitea, Code Server)
  - Home automation (Home Assistant)
  - Privacy tools (Pi-hole, AdGuard, WireGuard, Vaultwarden)
  - File storage (Nextcloud, Syncthing)
  - Monitoring (Uptime Kuma, Prometheus, Grafana)
  - And many more!

## 📋 Prerequisites

- Linux-based system (Ubuntu 20.04+ recommended)
- Python 3.8 or higher
- Docker and Docker Compose
- At least 2GB RAM and 20GB free disk space
- Internet connection

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/homelab-builder.git
cd homelab-builder
```

2. Run the installer:
```bash
chmod +x install.sh
./install.sh
```

The installer will:
- Check for required dependencies
- Install missing packages (with your permission)
- Set up a Python virtual environment
- Install all Python requirements
- Launch the interactive installer

## 🎯 Usage

### Quick Start

Simply run:
```bash
./install.sh
```

The interactive installer will guide you through:
1. **Environment Analysis**: Scans your system and network
2. **Requirements Gathering**: Asks about your use case and preferences
3. **Service Recommendations**: Suggests optimal services for your needs
4. **Deployment**: Automatically sets up all services

### Manual Installation

If you prefer to run the Python installer directly:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the installer
python installer/main.py
```

## 🏗️ Architecture

The project is organized into intelligent agents that handle different aspects:

```
homelab-builder/
├── agents/                 # Intelligent agents
│   ├── environment_scanner.py   # System analysis
│   ├── network_analyzer.py      # Network configuration
│   └── service_recommender.py   # AI recommendations
├── installer/              # Installation logic
│   ├── main.py            # Main installer
│   └── survey.py          # User survey
├── deployment/            # Deployment modules
│   └── deployer.py        # Docker Compose deployment
├── proxy/                 # Tunneling solutions
│   └── tunnel_manager.py  # VPN/proxy setup
├── services/              # Service templates
├── templates/             # Configuration templates
└── utils/                 # Utilities
    ├── config_manager.py  # Configuration handling
    └── logger.py          # Logging setup
```

## 🔧 Configuration

After installation, your homelab configuration will be saved to:
- Main config: `/opt/homelab/configs/homelab_config.json`
- Docker Compose: `/opt/homelab/docker-compose.yml`
- Service data: `/opt/homelab/data/`
- Logs: `/opt/homelab/logs/`

## 🔒 Security Features

- **Automated SSL/TLS**: Let's Encrypt integration for HTTPS
- **Authentication Options**: Basic auth, OAuth2, 2FA support
- **Firewall Configuration**: Automatic firewall rules
- **VPN Support**: WireGuard VPN for secure remote access
- **Security Monitoring**: Optional IDS/IPS with CrowdSec
- **Encrypted Backups**: Automated encrypted backups

## 📚 Supported Services

### Media & Entertainment
- Jellyfin - Open-source media server
- Plex - Popular media server with apps

### Development
- GitLab - Complete DevOps platform
- Gitea - Lightweight Git service
- Code Server - VS Code in browser

### Home Automation
- Home Assistant - Home automation platform

### Privacy & Security
- Pi-hole - Network-wide ad blocker
- AdGuard Home - Advanced ad blocker
- WireGuard - Modern VPN server
- Vaultwarden - Password manager
- Authelia - Authentication server

### Storage & Backup
- Nextcloud - Self-hosted cloud
- Syncthing - File synchronization
- Duplicati - Backup solution

### Monitoring
- Uptime Kuma - Uptime monitoring
- Prometheus - Metrics collection
- Grafana - Data visualization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- All the amazing open-source projects that make homelabs possible
- The self-hosting community for inspiration and feedback

## 📞 Support

- Create an issue for bug reports or feature requests
- Join our Discord community (coming soon)
- Check the [Wiki](https://github.com/yourusername/homelab-builder/wiki) for detailed documentation

---

Made with ❤️ by the Homelab Builder Team

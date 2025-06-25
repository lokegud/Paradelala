#!/usr/bin/env python3
"""
Network Scanner Agent
Scans the local network environment to discover available resources and topology
"""

import json
import socket
import subprocess
import sys
from typing import Dict, List, Any
import netifaces
import psutil
import nmap
import requests
from datetime import datetime


class NetworkScanner:
    """AI-powered network scanner to analyze network environment"""
    
    def __init__(self):
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "network_interfaces": {},
            "routing_table": [],
            "open_ports": {},
            "external_ip": None,
            "dns_servers": [],
            "network_speed": {},
            "discovered_services": [],
            "security_assessment": {}
        }
        
    def scan_network_interfaces(self) -> Dict[str, Any]:
        """Scan all network interfaces and their configurations"""
        interfaces = {}
        
        for iface in netifaces.interfaces():
            if iface == 'lo':  # Skip loopback
                continue
                
            iface_info = {
                "name": iface,
                "addresses": {},
                "status": "unknown",
                "mtu": None,
                "statistics": {}
            }
            
            # Get addresses
            addrs = netifaces.ifaddresses(iface)
            
            # IPv4 addresses
            if netifaces.AF_INET in addrs:
                iface_info["addresses"]["ipv4"] = addrs[netifaces.AF_INET]
            
            # IPv6 addresses
            if netifaces.AF_INET6 in addrs:
                iface_info["addresses"]["ipv6"] = addrs[netifaces.AF_INET6]
            
            # MAC address
            if netifaces.AF_LINK in addrs:
                iface_info["addresses"]["mac"] = addrs[netifaces.AF_LINK]
            
            # Get interface statistics
            stats = psutil.net_if_stats().get(iface)
            if stats:
                iface_info["status"] = "up" if stats.isup else "down"
                iface_info["mtu"] = stats.mtu
                iface_info["speed"] = stats.speed
            
            # Get traffic statistics
            io_counters = psutil.net_io_counters(pernic=True).get(iface)
            if io_counters:
                iface_info["statistics"] = {
                    "bytes_sent": io_counters.bytes_sent,
                    "bytes_recv": io_counters.bytes_recv,
                    "packets_sent": io_counters.packets_sent,
                    "packets_recv": io_counters.packets_recv,
                    "errors_in": io_counters.errin,
                    "errors_out": io_counters.errout,
                    "drops_in": io_counters.dropin,
                    "drops_out": io_counters.dropout
                }
            
            interfaces[iface] = iface_info
            
        return interfaces
    
    def get_routing_table(self) -> List[Dict[str, str]]:
        """Get system routing table"""
        routes = []
        
        try:
            # Get default gateway
            gateways = netifaces.gateways()
            default_gateway = gateways.get('default', {}).get(netifaces.AF_INET)
            
            if default_gateway:
                routes.append({
                    "destination": "0.0.0.0/0",
                    "gateway": default_gateway[0],
                    "interface": default_gateway[1],
                    "type": "default"
                })
            
            # Get additional routes using ip command
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith('default'):
                        parts = line.split()
                        if len(parts) >= 3:
                            routes.append({
                                "destination": parts[0],
                                "gateway": parts[2] if parts[1] == 'via' else "direct",
                                "interface": parts[-1] if 'dev' in parts else "unknown",
                                "type": "static"
                            })
        except Exception as e:
            routes.append({"error": str(e)})
            
        return routes
    
    def scan_open_ports(self, target: str = "127.0.0.1") -> Dict[int, Dict[str, str]]:
        """Scan for open ports on the system"""
        open_ports = {}
        
        # Get listening ports using psutil
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            if conn.status == 'LISTEN':
                port = conn.laddr.port
                open_ports[port] = {
                    "state": "open",
                    "service": self._identify_service(port),
                    "pid": conn.pid if conn.pid else "unknown",
                    "address": conn.laddr.ip
                }
        
        # Try nmap for more detailed scan (if available)
        try:
            nm = nmap.PortScanner()
            nm.scan(target, '1-65535', '-sV --version-intensity 0')
            
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        if port not in open_ports:
                            open_ports[port] = {
                                "state": nm[host][proto][port]['state'],
                                "service": nm[host][proto][port].get('name', 'unknown'),
                                "version": nm[host][proto][port].get('version', ''),
                                "address": host
                            }
        except Exception:
            # Nmap might not be available or might require root
            pass
            
        return open_ports
    
    def _identify_service(self, port: int) -> str:
        """Identify common services by port number"""
        common_ports = {
            22: "ssh",
            80: "http",
            443: "https",
            3306: "mysql",
            5432: "postgresql",
            6379: "redis",
            8080: "http-alt",
            9090: "prometheus",
            3000: "grafana",
            9100: "node-exporter",
            51820: "wireguard"
        }
        return common_ports.get(port, "unknown")
    
    def get_external_ip(self) -> str:
        """Get external IP address"""
        try:
            # Try multiple services for redundancy
            services = [
                "https://api.ipify.org?format=json",
                "https://ipinfo.io/json",
                "https://api.myip.com"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('ip', data.get('origin', 'unknown'))
                except Exception:
                    continue
                    
            return "unable to determine"
        except Exception:
            return "error"
    
    def get_dns_servers(self) -> List[str]:
        """Get configured DNS servers"""
        dns_servers = []
        
        try:
            # Read from resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
        except Exception:
            pass
            
        # Also check systemd-resolved if available
        try:
            result = subprocess.run(['systemd-resolve', '--status'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'DNS Servers:' in line:
                        dns_servers.extend(line.split(':')[1].strip().split())
        except Exception:
            pass
            
        return list(set(dns_servers))  # Remove duplicates
    
    def test_network_speed(self) -> Dict[str, float]:
        """Test network speed (basic ping test)"""
        speed_test = {
            "latency_google": None,
            "latency_cloudflare": None,
            "packet_loss": None
        }
        
        try:
            # Ping Google DNS
            result = subprocess.run(['ping', '-c', '4', '8.8.8.8'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'avg' in line:
                        speed_test["latency_google"] = float(line.split('/')[4])
                        
            # Ping Cloudflare DNS
            result = subprocess.run(['ping', '-c', '4', '1.1.1.1'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'avg' in line:
                        speed_test["latency_cloudflare"] = float(line.split('/')[4])
                    if 'packet loss' in line:
                        loss = line.split(',')[2].split('%')[0].strip()
                        speed_test["packet_loss"] = float(loss)
        except Exception:
            pass
            
        return speed_test
    
    def discover_services(self) -> List[Dict[str, Any]]:
        """Discover running services that might be useful for home lab"""
        services = []
        
        # Check for common services
        service_checks = [
            ("docker", "systemctl is-active docker"),
            ("nginx", "systemctl is-active nginx"),
            ("apache2", "systemctl is-active apache2"),
            ("mysql", "systemctl is-active mysql"),
            ("postgresql", "systemctl is-active postgresql"),
            ("redis", "systemctl is-active redis"),
            ("prometheus", "systemctl is-active prometheus"),
            ("grafana", "systemctl is-active grafana-server"),
            ("wireguard", "systemctl is-active wg-quick@wg0")
        ]
        
        for service_name, check_cmd in service_checks:
            try:
                result = subprocess.run(check_cmd.split(), 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip() == "active":
                    services.append({
                        "name": service_name,
                        "status": "active",
                        "type": "systemd"
                    })
            except Exception:
                pass
        
        # Check for Docker containers
        try:
            result = subprocess.run(['docker', 'ps', '--format', 'json'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    try:
                        container = json.loads(line)
                        services.append({
                            "name": container.get("Names", "unknown"),
                            "status": container.get("State", "unknown"),
                            "type": "docker",
                            "image": container.get("Image", "unknown"),
                            "ports": container.get("Ports", "")
                        })
                    except Exception:
                        pass
        except Exception:
            pass
            
        return services
    
    def assess_security(self) -> Dict[str, Any]:
        """Basic security assessment of the network"""
        assessment = {
            "firewall_enabled": False,
            "ssh_hardened": False,
            "unnecessary_services": [],
            "recommendations": []
        }
        
        # Check if firewall is enabled
        try:
            result = subprocess.run(['ufw', 'status'], 
                                  capture_output=True, text=True)
            if 'Status: active' in result.stdout:
                assessment["firewall_enabled"] = True
            else:
                assessment["recommendations"].append("Enable UFW firewall")
        except Exception:
            assessment["recommendations"].append("Install and configure UFW firewall")
        
        # Check SSH configuration
        try:
            with open('/etc/ssh/sshd_config', 'r') as f:
                sshd_config = f.read()
                
            if 'PermitRootLogin no' in sshd_config:
                assessment["ssh_hardened"] = True
            else:
                assessment["recommendations"].append("Disable root login in SSH")
                
            if 'PasswordAuthentication no' not in sshd_config:
                assessment["recommendations"].append(
                    "Consider disabling password authentication in SSH"
                )
        except Exception:
            pass
        
        # Check for unnecessary services
        risky_ports = {
            23: "telnet",
            135: "msrpc",
            139: "netbios",
            445: "smb",
            3389: "rdp"
        }
        
        for port, service in risky_ports.items():
            if port in self.scan_results.get("open_ports", {}):
                assessment["unnecessary_services"].append(f"{service} (port {port})")
                assessment["recommendations"].append(
                    f"Consider disabling {service} on port {port}"
                )
        
        return assessment
    
    def run_full_scan(self) -> Dict[str, Any]:
        """Run complete network scan"""
        print("Starting network environment scan...")
        
        # Scan network interfaces
        print("Scanning network interfaces...")
        self.scan_results["network_interfaces"] = self.scan_network_interfaces()
        
        # Get routing information
        print("Analyzing routing table...")
        self.scan_results["routing_table"] = self.get_routing_table()
        
        # Scan open ports
        print("Scanning open ports...")
        self.scan_results["open_ports"] = self.scan_open_ports()
        
        # Get external IP
        print("Determining external IP...")
        self.scan_results["external_ip"] = self.get_external_ip()
        
        # Get DNS servers
        print("Checking DNS configuration...")
        self.scan_results["dns_servers"] = self.get_dns_servers()
        
        # Test network speed
        print("Testing network connectivity...")
        self.scan_results["network_speed"] = self.test_network_speed()
        
        # Discover services
        print("Discovering running services...")
        self.scan_results["discovered_services"] = self.discover_services()
        
        # Security assessment
        print("Performing security assessment...")
        self.scan_results["security_assessment"] = self.assess_security()
        
        return self.scan_results


def main():
    """Main entry point"""
    scanner = NetworkScanner()
    results = scanner.run_full_scan()
    
    # Output results as JSON
    print(json.dumps(results, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

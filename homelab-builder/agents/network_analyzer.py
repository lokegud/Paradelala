#!/usr/bin/env python3
"""
Network Analyzer Agent
Analyzes network configuration, connectivity, and security settings.
"""

import socket
import subprocess
import requests
import netifaces
import ipaddress
from typing import Dict, Any, List, Optional
import json
import re
import shutil


class NetworkAnalyzer:
    """Agent responsible for analyzing network configuration and connectivity."""
    
    def __init__(self):
        self.analysis_results = {}
    
    def analyze(self) -> Dict[str, Any]:
        """Perform complete network analysis."""
        self.analysis_results = {
            'public_ip': self._get_public_ip(),
            'private_ips': self._get_private_ips(),
            'primary_interface': self._get_primary_interface(),
            'open_ports': self._scan_open_ports(),
            'firewall_active': self._check_firewall(),
            'dns_servers': self._get_dns_servers(),
            'gateway': self._get_default_gateway(),
            'network_speed': self._test_network_speed(),
            'vpn_detected': self._detect_vpn(),
            'nat_type': self._detect_nat_type(),
            'ipv6_support': self._check_ipv6_support()
        }
        return self.analysis_results
    
    def _get_public_ip(self) -> Optional[str]:
        """Get public IP address."""
        try:
            # Try multiple services for redundancy
            services = [
                'https://api.ipify.org?format=json',
                'https://ipapi.co/json/',
                'https://ifconfig.me/all.json'
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if 'ip' in data:
                            return data['ip']
                        elif 'ip_addr' in data:
                            return data['ip_addr']
                except:
                    continue
            
            # Fallback to simple text API
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
            
        except Exception as e:
            return None
    
    def _get_private_ips(self) -> Dict[str, List[str]]:
        """Get private IP addresses for all interfaces."""
        private_ips = {}
        
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if self._is_private_ip(ip):
                        if interface not in private_ips:
                            private_ips[interface] = []
                        private_ips[interface].append(ip)
        
        return private_ips
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if an IP address is private."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _get_primary_interface(self) -> Optional[str]:
        """Get the primary network interface."""
        try:
            # Get the interface used for the default route
            gateways = netifaces.gateways()
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                return gateways['default'][netifaces.AF_INET][1]
        except:
            pass
        
        # Fallback: find interface with most likely primary IP
        private_ips = self._get_private_ips()
        for interface, ips in private_ips.items():
            if interface not in ['lo', 'localhost']:
                return interface
        
        return None
    
    def _scan_open_ports(self) -> List[int]:
        """Scan for commonly used open ports."""
        open_ports = []
        common_ports = [22, 80, 443, 8080, 8443, 3000, 5000, 9090]
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        return open_ports
    
    def _check_firewall(self) -> Dict[str, Any]:
        """Check firewall status."""
        firewall_info = {
            'active': False,
            'type': None,
            'rules_count': 0
        }
        
        # Check UFW (Ubuntu Firewall)
        if shutil.which('ufw'):
            try:
                result = subprocess.run(['sudo', 'ufw', 'status'], 
                                      capture_output=True, text=True)
                if 'Status: active' in result.stdout:
                    firewall_info['active'] = True
                    firewall_info['type'] = 'ufw'
                    # Count rules
                    rules = result.stdout.count('ALLOW') + result.stdout.count('DENY')
                    firewall_info['rules_count'] = rules
            except:
                pass
        
        # Check iptables
        if not firewall_info['active'] and shutil.which('iptables'):
            try:
                result = subprocess.run(['sudo', 'iptables', '-L', '-n'], 
                                      capture_output=True, text=True)
                # Check if there are custom rules (not just default policies)
                if result.stdout.count('Chain') > 3:  # More than default chains
                    firewall_info['active'] = True
                    firewall_info['type'] = 'iptables'
            except:
                pass
        
        # Check firewalld
        if not firewall_info['active'] and shutil.which('firewall-cmd'):
            try:
                result = subprocess.run(['firewall-cmd', '--state'], 
                                      capture_output=True, text=True)
                if result.stdout.strip() == 'running':
                    firewall_info['active'] = True
                    firewall_info['type'] = 'firewalld'
            except:
                pass
        
        return firewall_info
    
    def _get_dns_servers(self) -> List[str]:
        """Get configured DNS servers."""
        dns_servers = []
        
        # Check resolv.conf
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns = line.split()[1]
                        if dns not in dns_servers:
                            dns_servers.append(dns)
        except:
            pass
        
        # Check systemd-resolved
        if shutil.which('systemd-resolve'):
            try:
                result = subprocess.run(['systemd-resolve', '--status'], 
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'DNS Servers:' in line:
                        dns = line.split(':')[1].strip()
                        if dns and dns not in dns_servers:
                            dns_servers.append(dns)
            except:
                pass
        
        return dns_servers
    
    def _get_default_gateway(self) -> Optional[str]:
        """Get default gateway."""
        try:
            gateways = netifaces.gateways()
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                return gateways['default'][netifaces.AF_INET][0]
        except:
            pass
        
        # Fallback to ip route command
        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            match = re.search(r'default via (\S+)', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        
        return None
    
    def _test_network_speed(self) -> Dict[str, Any]:
        """Test basic network connectivity and latency."""
        speed_info = {
            'latency_ms': None,
            'download_speed_estimate': None,
            'connectivity': 'unknown'
        }
        
        # Test connectivity and latency
        try:
            import time
            start = time.time()
            response = requests.get('https://www.google.com', timeout=5)
            end = time.time()
            
            if response.status_code == 200:
                speed_info['connectivity'] = 'good'
                speed_info['latency_ms'] = round((end - start) * 1000)
            else:
                speed_info['connectivity'] = 'limited'
        except requests.exceptions.Timeout:
            speed_info['connectivity'] = 'slow'
        except:
            speed_info['connectivity'] = 'offline'
        
        return speed_info
    
    def _detect_vpn(self) -> Dict[str, Any]:
        """Detect if VPN is active."""
        vpn_info = {
            'active': False,
            'type': None,
            'interface': None
        }
        
        # Check for common VPN interfaces
        vpn_interfaces = ['tun', 'tap', 'wg', 'ppp']
        interfaces = netifaces.interfaces()
        
        for interface in interfaces:
            for vpn_type in vpn_interfaces:
                if interface.startswith(vpn_type):
                    vpn_info['active'] = True
                    vpn_info['interface'] = interface
                    if vpn_type == 'wg':
                        vpn_info['type'] = 'WireGuard'
                    elif vpn_type in ['tun', 'tap']:
                        vpn_info['type'] = 'OpenVPN'
                    elif vpn_type == 'ppp':
                        vpn_info['type'] = 'PPTP/L2TP'
                    break
        
        # Check for WireGuard specifically
        if not vpn_info['active'] and shutil.which('wg'):
            try:
                result = subprocess.run(['wg', 'show'], capture_output=True, text=True)
                if result.stdout.strip():
                    vpn_info['active'] = True
                    vpn_info['type'] = 'WireGuard'
            except:
                pass
        
        return vpn_info
    
    def _detect_nat_type(self) -> str:
        """Detect NAT type (simplified detection)."""
        # This is a simplified NAT detection
        # Full STUN-based detection would require more complex implementation
        
        public_ip = self.analysis_results.get('public_ip')
        private_ips = self.analysis_results.get('private_ips', {})
        
        if not public_ip:
            return 'unknown'
        
        if private_ips:
            # We're behind NAT
            return 'symmetric'  # Most common for home/office networks
        else:
            # Direct connection (rare for home users)
            return 'open'
    
    def _check_ipv6_support(self) -> Dict[str, Any]:
        """Check IPv6 support."""
        ipv6_info = {
            'supported': False,
            'addresses': [],
            'connectivity': False
        }
        
        # Check for IPv6 addresses
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET6 in addrs:
                for addr in addrs[netifaces.AF_INET6]:
                    ip = addr['addr']
                    # Filter out link-local addresses
                    if not ip.startswith('fe80:'):
                        ipv6_info['supported'] = True
                        ipv6_info['addresses'].append({
                            'interface': interface,
                            'address': ip
                        })
        
        # Test IPv6 connectivity
        if ipv6_info['supported']:
            try:
                socket.create_connection(('ipv6.google.com', 80), timeout=2)
                ipv6_info['connectivity'] = True
            except:
                pass
        
        return ipv6_info
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the network analysis."""
        if not self.analysis_results:
            return "No analysis results available. Run analyze() first."
        
        summary = []
        summary.append(f"Public IP: {self.analysis_results.get('public_ip', 'Unknown')}")
        summary.append(f"Primary Interface: {self.analysis_results.get('primary_interface', 'Unknown')}")
        summary.append(f"Gateway: {self.analysis_results.get('gateway', 'Unknown')}")
        
        firewall = self.analysis_results.get('firewall_active', {})
        if isinstance(firewall, dict) and firewall.get('active'):
            summary.append(f"Firewall: Active ({firewall.get('type', 'unknown')})")
        else:
            summary.append("Firewall: Inactive")
        
        vpn = self.analysis_results.get('vpn_detected', {})
        if vpn.get('active'):
            summary.append(f"VPN: Active ({vpn.get('type', 'unknown')})")
        
        open_ports = self.analysis_results.get('open_ports', [])
        if open_ports:
            summary.append(f"Open Ports: {', '.join(map(str, open_ports))}")
        
        return "\n".join(summary)


if __name__ == "__main__":
    # Test the analyzer
    analyzer = NetworkAnalyzer()
    results = analyzer.analyze()
    print(json.dumps(results, indent=2))
    print("\n" + "="*50 + "\n")
    print(analyzer.get_summary())

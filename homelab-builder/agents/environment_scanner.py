#!/usr/bin/env python3
"""
Environment Scanner Agent
Scans and analyzes the system environment including OS, resources, and installed software.
"""

import os
import platform
import subprocess
import psutil
import json
from typing import Dict, Any, List
import distro
import shutil


class EnvironmentScanner:
    """Agent responsible for scanning the system environment."""
    
    def __init__(self):
        self.scan_results = {}
    
    def scan(self) -> Dict[str, Any]:
        """Perform a complete environment scan."""
        self.scan_results = {
            'os_info': self._get_os_info(),
            'cpu_count': self._get_cpu_info(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info(),
            'docker': self._check_docker(),
            'network_interfaces': self._get_network_interfaces(),
            'installed_packages': self._get_installed_packages(),
            'kernel_info': self._get_kernel_info(),
            'virtualization': self._detect_virtualization(),
            'system_services': self._get_system_services()
        }
        return self.scan_results
    
    def _get_os_info(self) -> Dict[str, str]:
        """Get operating system information."""
        try:
            info = {
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
            
            # Get more detailed info for Linux
            if platform.system() == 'Linux':
                dist_info = distro.info()
                info.update({
                    'distribution': dist_info.get('id', 'unknown'),
                    'distribution_version': dist_info.get('version', 'unknown'),
                    'distribution_codename': dist_info.get('codename', 'unknown')
                })
            
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def _get_cpu_info(self) -> int:
        """Get CPU information."""
        return psutil.cpu_count(logical=True)
    
    def _get_memory_info(self) -> Dict[str, float]:
        """Get memory information."""
        mem = psutil.virtual_memory()
        return {
            'total_gb': mem.total / (1024**3),
            'available_gb': mem.available / (1024**3),
            'used_gb': mem.used / (1024**3),
            'percent': mem.percent
        }
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk space information."""
        disk = psutil.disk_usage('/')
        return {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': disk.percent,
            'partitions': self._get_disk_partitions()
        }
    
    def _get_disk_partitions(self) -> List[Dict[str, Any]]:
        """Get information about disk partitions."""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': usage.total / (1024**3),
                    'free_gb': usage.free / (1024**3)
                })
            except PermissionError:
                continue
        return partitions
    
    def _check_docker(self) -> Dict[str, Any]:
        """Check if Docker is installed and get version."""
        docker_info = {
            'installed': False,
            'version': None,
            'compose_installed': False,
            'compose_version': None,
            'running': False
        }
        
        # Check Docker
        if shutil.which('docker'):
            docker_info['installed'] = True
            try:
                version = subprocess.check_output(['docker', '--version'], text=True).strip()
                docker_info['version'] = version
                
                # Check if Docker daemon is running
                subprocess.check_output(['docker', 'ps'], stderr=subprocess.DEVNULL)
                docker_info['running'] = True
            except subprocess.CalledProcessError:
                docker_info['running'] = False
        
        # Check Docker Compose
        if shutil.which('docker-compose'):
            docker_info['compose_installed'] = True
            try:
                version = subprocess.check_output(['docker-compose', '--version'], text=True).strip()
                docker_info['compose_version'] = version
            except subprocess.CalledProcessError:
                pass
        
        return docker_info
    
    def _get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information."""
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {
                'name': interface,
                'addresses': []
            }
            for addr in addrs:
                addr_info = {
                    'family': str(addr.family),
                    'address': addr.address
                }
                if addr.netmask:
                    addr_info['netmask'] = addr.netmask
                if addr.broadcast:
                    addr_info['broadcast'] = addr.broadcast
                interface_info['addresses'].append(addr_info)
            interfaces.append(interface_info)
        return interfaces
    
    def _get_installed_packages(self) -> Dict[str, bool]:
        """Check for commonly needed packages."""
        packages = {
            'git': shutil.which('git') is not None,
            'curl': shutil.which('curl') is not None,
            'wget': shutil.which('wget') is not None,
            'python3': shutil.which('python3') is not None,
            'pip': shutil.which('pip3') is not None,
            'systemctl': shutil.which('systemctl') is not None,
            'ufw': shutil.which('ufw') is not None,
            'iptables': shutil.which('iptables') is not None,
            'nginx': shutil.which('nginx') is not None,
            'certbot': shutil.which('certbot') is not None
        }
        return packages
    
    def _get_kernel_info(self) -> Dict[str, str]:
        """Get kernel information."""
        try:
            kernel_info = {
                'version': platform.release(),
                'full_version': platform.version()
            }
            
            # Get more detailed kernel info on Linux
            if platform.system() == 'Linux':
                try:
                    with open('/proc/version', 'r') as f:
                        kernel_info['proc_version'] = f.read().strip()
                except:
                    pass
            
            return kernel_info
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_virtualization(self) -> Dict[str, Any]:
        """Detect if running in a virtualized environment."""
        virt_info = {
            'is_virtual': False,
            'type': 'physical',
            'hypervisor': None
        }
        
        if platform.system() == 'Linux':
            # Check systemd-detect-virt
            if shutil.which('systemd-detect-virt'):
                try:
                    result = subprocess.check_output(['systemd-detect-virt'], text=True).strip()
                    if result and result != 'none':
                        virt_info['is_virtual'] = True
                        virt_info['type'] = 'virtual'
                        virt_info['hypervisor'] = result
                except subprocess.CalledProcessError:
                    pass
            
            # Check for common virtualization files
            virt_files = {
                '/proc/xen': 'xen',
                '/sys/hypervisor/type': 'xen',
                '/proc/modules': 'check_content'
            }
            
            for file_path, virt_type in virt_files.items():
                if os.path.exists(file_path):
                    if virt_type == 'check_content':
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                if 'vboxdrv' in content:
                                    virt_info['is_virtual'] = True
                                    virt_info['type'] = 'virtual'
                                    virt_info['hypervisor'] = 'virtualbox'
                                elif 'vmware' in content:
                                    virt_info['is_virtual'] = True
                                    virt_info['type'] = 'virtual'
                                    virt_info['hypervisor'] = 'vmware'
                        except:
                            pass
                    else:
                        virt_info['is_virtual'] = True
                        virt_info['type'] = 'virtual'
                        virt_info['hypervisor'] = virt_type
        
        return virt_info
    
    def _get_system_services(self) -> Dict[str, bool]:
        """Check status of important system services."""
        services = {}
        
        if shutil.which('systemctl'):
            service_list = ['ssh', 'sshd', 'nginx', 'apache2', 'httpd', 'docker', 'firewalld', 'ufw']
            for service in service_list:
                try:
                    result = subprocess.run(
                        ['systemctl', 'is-active', service],
                        capture_output=True,
                        text=True
                    )
                    services[service] = result.stdout.strip() == 'active'
                except:
                    services[service] = False
        
        return services
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the scan results."""
        if not self.scan_results:
            return "No scan results available. Run scan() first."
        
        summary = []
        summary.append(f"OS: {self.scan_results['os_info']['system']} {self.scan_results['os_info']['release']}")
        summary.append(f"CPU Cores: {self.scan_results['cpu_count']}")
        summary.append(f"Memory: {self.scan_results['memory']['total_gb']:.2f} GB total, {self.scan_results['memory']['available_gb']:.2f} GB available")
        summary.append(f"Disk: {self.scan_results['disk']['free_gb']:.2f} GB free of {self.scan_results['disk']['total_gb']:.2f} GB")
        summary.append(f"Docker: {'Installed' if self.scan_results['docker']['installed'] else 'Not installed'}")
        
        if self.scan_results['virtualization']['is_virtual']:
            summary.append(f"Virtualization: {self.scan_results['virtualization']['hypervisor']}")
        
        return "\n".join(summary)


if __name__ == "__main__":
    # Test the scanner
    scanner = EnvironmentScanner()
    results = scanner.scan()
    print(json.dumps(results, indent=2))
    print("\n" + "="*50 + "\n")
    print(scanner.get_summary())

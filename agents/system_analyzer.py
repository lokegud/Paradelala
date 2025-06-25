#!/usr/bin/env python3
"""
System Analyzer Agent
Analyzes system capabilities, resources, and performance characteristics
"""

import json
import os
import platform
import subprocess
import sys
from typing import Dict, List, Any, Tuple
import psutil
import cpuinfo
from datetime import datetime
import distro


class SystemAnalyzer:
    """AI-powered system analyzer to assess system capabilities"""
    
    def __init__(self):
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "hardware": {},
            "resources": {},
            "performance": {},
            "installed_software": {},
            "capabilities": {},
            "recommendations": []
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        system_info = {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        
        # Get distribution info for Linux
        if platform.system() == "Linux":
            dist_info = distro.info()
            system_info["distribution"] = {
                "name": dist_info.get("id", "unknown"),
                "version": dist_info.get("version", "unknown"),
                "codename": dist_info.get("codename", "unknown"),
                "like": dist_info.get("like", "unknown")
            }
        
        # Get kernel parameters
        try:
            with open('/proc/cmdline', 'r') as f:
                system_info["kernel_cmdline"] = f.read().strip()
        except Exception:
            pass
        
        # Get system uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        system_info["boot_time"] = boot_time.isoformat()
        system_info["uptime_seconds"] = int((datetime.now() - boot_time).total_seconds())
        
        return system_info
    
    def analyze_hardware(self) -> Dict[str, Any]:
        """Analyze hardware capabilities"""
        hardware = {}
        
        # CPU Information
        cpu_info = cpuinfo.get_cpu_info()
        hardware["cpu"] = {
            "brand": cpu_info.get("brand_raw", "unknown"),
            "architecture": cpu_info.get("arch", "unknown"),
            "bits": cpu_info.get("bits", 0),
            "count": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "frequency": {
                "current": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "min": psutil.cpu_freq().min if psutil.cpu_freq() else 0,
                "max": psutil.cpu_freq().max if psutil.cpu_freq() else 0
            },
            "features": cpu_info.get("flags", [])[:20]  # Limit features list
        }
        
        # Memory Information
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        hardware["memory"] = {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent
        }
        
        # Disk Information
        hardware["disks"] = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                hardware["disks"].append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except Exception:
                continue
        
        # Network Interfaces
        hardware["network_interfaces"] = []
        for iface, addrs in psutil.net_if_addrs().items():
            iface_info = {
                "name": iface,
                "addresses": []
            }
            for addr in addrs:
                iface_info["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            hardware["network_interfaces"].append(iface_info)
        
        return hardware
    
    def analyze_resources(self) -> Dict[str, Any]:
        """Analyze current resource usage"""
        resources = {}
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        resources["cpu_usage"] = {
            "overall": sum(cpu_percent) / len(cpu_percent),
            "per_core": cpu_percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
        
        # Memory Usage
        mem = psutil.virtual_memory()
        resources["memory_usage"] = {
            "used_gb": mem.used / (1024**3),
            "available_gb": mem.available / (1024**3),
            "percent": mem.percent,
            "buffers": getattr(mem, 'buffers', 0),
            "cached": getattr(mem, 'cached', 0)
        }
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            resources["disk_io"] = {
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count
            }
        
        # Network I/O
        net_io = psutil.net_io_counters()
        resources["network_io"] = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        # Process Information
        resources["processes"] = {
            "total": len(psutil.pids()),
            "running": len([p for p in psutil.process_iter(['status']) 
                          if p.info['status'] == psutil.STATUS_RUNNING])
        }
        
        return resources
    
    def test_performance(self) -> Dict[str, Any]:
        """Run basic performance tests"""
        performance = {}
        
        # CPU Performance Test (simple calculation)
        import time
        start_time = time.time()
        # Simple CPU benchmark
        result = sum(i * i for i in range(1000000))
        cpu_time = time.time() - start_time
        performance["cpu_benchmark"] = {
            "time_seconds": cpu_time,
            "operations": 1000000,
            "ops_per_second": 1000000 / cpu_time
        }
        
        # Memory bandwidth test (simple)
        start_time = time.time()
        data = bytearray(10 * 1024 * 1024)  # 10MB
        for i in range(len(data)):
            data[i] = i % 256
        mem_time = time.time() - start_time
        performance["memory_bandwidth"] = {
            "time_seconds": mem_time,
            "size_mb": 10,
            "bandwidth_mbps": 10 / mem_time
        }
        
        # Disk performance (if possible)
        try:
            test_file = "/tmp/disk_test_file"
            data = os.urandom(10 * 1024 * 1024)  # 10MB
            
            # Write test
            start_time = time.time()
            with open(test_file, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            write_time = time.time() - start_time
            
            # Read test
            start_time = time.time()
            with open(test_file, 'rb') as f:
                _ = f.read()
            read_time = time.time() - start_time
            
            os.remove(test_file)
            
            performance["disk_performance"] = {
                "write_mbps": 10 / write_time,
                "read_mbps": 10 / read_time
            }
        except Exception:
            performance["disk_performance"] = {"error": "Unable to test"}
        
        return performance
    
    def check_installed_software(self) -> Dict[str, Any]:
        """Check for installed software relevant to home lab"""
        software = {
            "package_managers": [],
            "containerization": {},
            "web_servers": {},
            "databases": {},
            "monitoring": {},
            "security": {},
            "development": {}
        }
        
        # Check package managers
        package_managers = [
            ("apt", "apt --version"),
            ("yum", "yum --version"),
            ("dnf", "dnf --version"),
            ("pacman", "pacman --version"),
            ("snap", "snap --version"),
            ("flatpak", "flatpak --version")
        ]
        
        for name, cmd in package_managers:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    software["package_managers"].append({
                        "name": name,
                        "version": result.stdout.strip().split('\n')[0]
                    })
            except Exception:
                pass
        
        # Check containerization tools
        container_tools = [
            ("docker", "docker --version"),
            ("podman", "podman --version"),
            ("lxc", "lxc --version"),
            ("kubectl", "kubectl version --client --short")
        ]
        
        for name, cmd in container_tools:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    software["containerization"][name] = {
                        "installed": True,
                        "version": result.stdout.strip()
                    }
            except Exception:
                software["containerization"][name] = {"installed": False}
        
        # Check web servers
        web_servers = [
            ("nginx", "nginx -v"),
            ("apache2", "apache2 -v"),
            ("caddy", "caddy version")
        ]
        
        for name, cmd in web_servers:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, 
                                      text=True, stderr=subprocess.STDOUT)
                if result.returncode == 0 or name in result.stdout:
                    software["web_servers"][name] = {
                        "installed": True,
                        "version": result.stdout.strip()
                    }
            except Exception:
                software["web_servers"][name] = {"installed": False}
        
        # Check databases
        databases = [
            ("mysql", "mysql --version"),
            ("postgresql", "psql --version"),
            ("redis", "redis-server --version"),
            ("mongodb", "mongod --version")
        ]
        
        for name, cmd in databases:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    software["databases"][name] = {
                        "installed": True,
                        "version": result.stdout.strip()
                    }
            except Exception:
                software["databases"][name] = {"installed": False}
        
        return software
    
    def assess_capabilities(self) -> Dict[str, Any]:
        """Assess system capabilities for home lab deployment"""
        capabilities = {
            "virtualization": {},
            "containerization": {},
            "networking": {},
            "security": {},
            "suitable_services": []
        }
        
        # Check virtualization support
        try:
            # Check CPU virtualization extensions
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                capabilities["virtualization"]["vmx"] = "vmx" in cpuinfo
                capabilities["virtualization"]["svm"] = "svm" in cpuinfo
            
            # Check if running in a VM
            result = subprocess.run(['systemd-detect-virt'], 
                                  capture_output=True, text=True)
            capabilities["virtualization"]["is_virtual"] = result.returncode == 0
            capabilities["virtualization"]["virt_type"] = result.stdout.strip()
        except Exception:
            pass
        
        # Check containerization readiness
        capabilities["containerization"]["docker_ready"] = (
            self.analysis_results["installed_software"]["containerization"]
            .get("docker", {}).get("installed", False)
        )
        
        # Check networking capabilities
        capabilities["networking"]["ipv6_enabled"] = os.path.exists('/proc/net/if_inet6')
        capabilities["networking"]["ip_forwarding"] = False
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'r') as f:
                capabilities["networking"]["ip_forwarding"] = f.read().strip() == "1"
        except Exception:
            pass
        
        # Determine suitable services based on resources
        mem_gb = self.analysis_results["hardware"]["memory"]["total"] / (1024**3)
        cpu_cores = self.analysis_results["hardware"]["cpu"]["threads"]
        
        if mem_gb >= 8 and cpu_cores >= 4:
            capabilities["suitable_services"].extend([
                "kubernetes", "openstack", "proxmox"
            ])
        if mem_gb >= 4:
            capabilities["suitable_services"].extend([
                "docker-swarm", "portainer", "gitlab"
            ])
        if mem_gb >= 2:
            capabilities["suitable_services"].extend([
                "nextcloud", "plex", "home-assistant"
            ])
        
        capabilities["suitable_services"].extend([
            "pihole", "wireguard", "nginx-proxy-manager"
        ])
        
        return capabilities
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Memory recommendations
        mem_gb = self.analysis_results["hardware"]["memory"]["total"] / (1024**3)
        if mem_gb < 2:
            recommendations.append(
                "System has limited memory. Consider lightweight services only."
            )
        elif mem_gb < 4:
            recommendations.append(
                "Memory is adequate for basic services. Avoid memory-intensive applications."
            )
        
        # CPU recommendations
        cpu_usage = self.analysis_results["resources"]["cpu_usage"]["overall"]
        if cpu_usage > 80:
            recommendations.append(
                "High CPU usage detected. Consider optimizing existing services."
            )
        
        # Disk recommendations
        for disk in self.analysis_results["hardware"]["disks"]:
            if disk["percent"] > 80:
                recommendations.append(
                    f"Disk {disk['device']} is {disk['percent']}% full. Consider cleanup."
                )
        
        # Security recommendations
        if not self.analysis_results["installed_software"]["security"].get("ufw", {}).get("installed", False):
            recommendations.append("Install and configure UFW firewall for security.")
        
        # Container recommendations
        if not self.analysis_results["capabilities"]["containerization"]["docker_ready"]:
            recommendations.append("Install Docker for container-based deployments.")
        
        return recommendations
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete system analysis"""
        print("Starting system analysis...")
        
        # Get system information
        print("Gathering system information...")
        self.analysis_results["system_info"] = self.get_system_info()
        
        # Analyze hardware
        print("Analyzing hardware capabilities...")
        self.analysis_results["hardware"] = self.analyze_hardware()
        
        # Analyze resources
        print("Analyzing resource usage...")
        self.analysis_results["resources"] = self.analyze_resources()
        
        # Test performance
        print("Running performance tests...")
        self.analysis_results["performance"] = self.test_performance()
        
        # Check installed software
        print("Checking installed software...")
        self.analysis_results["installed_software"] = self.check_installed_software()
        
        # Assess capabilities
        print("Assessing system capabilities...")
        self.analysis_results["capabilities"] = self.assess_capabilities()
        
        # Generate recommendations
        print("Generating recommendations...")
        self.analysis_results["recommendations"] = self.generate_recommendations()
        
        return self.analysis_results


def main():
    """Main entry point"""
    analyzer = SystemAnalyzer()
    results = analyzer.run_full_analysis()
    
    # Output results as JSON
    print(json.dumps(results, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

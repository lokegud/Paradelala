#!/usr/bin/env python3
"""
Security Auditor Agent
Performs security assessment and provides recommendations for hardening
"""

import json
import os
import subprocess
import sys
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pwd
import grp
import stat


class SecurityAuditor:
    """AI-powered security auditor for system security assessment"""
    
    def __init__(self):
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "security_score": 0,
            "vulnerabilities": [],
            "misconfigurations": [],
            "compliance": {},
            "hardening_status": {},
            "recommendations": [],
            "critical_issues": []
        }
        self.total_checks = 0
        self.passed_checks = 0
    
    def calculate_score(self):
        """Calculate overall security score"""
        if self.total_checks > 0:
            self.audit_results["security_score"] = int(
                (self.passed_checks / self.total_checks) * 100
            )
    
    def check_user_accounts(self) -> Dict[str, Any]:
        """Audit user accounts and permissions"""
        user_audit = {
            "total_users": 0,
            "system_users": 0,
            "regular_users": 0,
            "users_with_empty_passwords": [],
            "users_with_uid_0": [],
            "inactive_users": [],
            "sudo_users": []
        }
        
        # Check /etc/passwd
        try:
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 7:
                        username = parts[0]
                        uid = int(parts[2])
                        shell = parts[6]
                        
                        user_audit["total_users"] += 1
                        
                        if uid < 1000:
                            user_audit["system_users"] += 1
                        else:
                            user_audit["regular_users"] += 1
                        
                        # Check for additional root users
                        if uid == 0 and username != "root":
                            user_audit["users_with_uid_0"].append(username)
                            self.audit_results["critical_issues"].append(
                                f"User {username} has UID 0 (root privileges)"
                            )
                        
                        # Check for valid login shells
                        if shell not in ['/bin/false', '/usr/sbin/nologin', '/bin/nologin']:
                            if uid < 1000 and username not in ['root', 'sync']:
                                self.audit_results["misconfigurations"].append(
                                    f"System user {username} has valid shell: {shell}"
                                )
        except Exception as e:
            self.audit_results["vulnerabilities"].append(
                f"Unable to read /etc/passwd: {str(e)}"
            )
        
        # Check /etc/shadow for empty passwords
        try:
            with open('/etc/shadow', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        username = parts[0]
                        password = parts[1]
                        
                        if password == "" or password == "!":
                            user_audit["users_with_empty_passwords"].append(username)
                            self.audit_results["critical_issues"].append(
                                f"User {username} has empty password"
                            )
        except Exception:
            # Need root to read shadow file
            pass
        
        # Check sudo users
        try:
            result = subprocess.run(['getent', 'group', 'sudo'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                sudo_users = result.stdout.strip().split(':')[-1].split(',')
                user_audit["sudo_users"] = [u for u in sudo_users if u]
        except Exception:
            pass
        
        self.total_checks += 3
        if not user_audit["users_with_uid_0"]:
            self.passed_checks += 1
        if not user_audit["users_with_empty_passwords"]:
            self.passed_checks += 1
        if user_audit["regular_users"] < 10:  # Arbitrary threshold
            self.passed_checks += 1
        
        return user_audit
    
    def check_file_permissions(self) -> Dict[str, Any]:
        """Check critical file permissions"""
        permission_audit = {
            "world_writable_files": [],
            "suid_files": [],
            "sgid_files": [],
            "critical_file_permissions": {}
        }
        
        # Critical files to check
        critical_files = {
            "/etc/passwd": 0o644,
            "/etc/shadow": 0o640,
            "/etc/group": 0o644,
            "/etc/gshadow": 0o640,
            "/etc/ssh/sshd_config": 0o600,
            "/etc/sudoers": 0o440,
            "/boot/grub/grub.cfg": 0o600,
            "/etc/crontab": 0o600
        }
        
        for filepath, expected_perms in critical_files.items():
            try:
                stat_info = os.stat(filepath)
                actual_perms = stat.S_IMODE(stat_info.st_mode)
                
                permission_audit["critical_file_permissions"][filepath] = {
                    "expected": oct(expected_perms),
                    "actual": oct(actual_perms),
                    "correct": actual_perms == expected_perms
                }
                
                if actual_perms != expected_perms:
                    self.audit_results["misconfigurations"].append(
                        f"{filepath} has permissions {oct(actual_perms)}, "
                        f"expected {oct(expected_perms)}"
                    )
                else:
                    self.passed_checks += 1
                
                self.total_checks += 1
            except Exception:
                pass
        
        # Find world-writable files (limited search)
        try:
            result = subprocess.run(
                ['find', '/etc', '/usr', '/bin', '/sbin', '-type', 'f', 
                 '-perm', '-002', '-ls'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout:
                files = result.stdout.strip().split('\n')
                permission_audit["world_writable_files"] = files[:20]  # Limit results
                if files:
                    self.audit_results["vulnerabilities"].append(
                        f"Found {len(files)} world-writable files"
                    )
        except Exception:
            pass
        
        # Find SUID/SGID files
        try:
            # SUID files
            result = subprocess.run(
                ['find', '/', '-type', 'f', '-perm', '-4000', '-ls'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout:
                permission_audit["suid_files"] = result.stdout.strip().split('\n')[:20]
            
            # SGID files
            result = subprocess.run(
                ['find', '/', '-type', 'f', '-perm', '-2000', '-ls'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout:
                permission_audit["sgid_files"] = result.stdout.strip().split('\n')[:20]
        except Exception:
            pass
        
        return permission_audit
    
    def check_network_security(self) -> Dict[str, Any]:
        """Check network security configuration"""
        network_audit = {
            "firewall_status": "unknown",
            "open_ports": [],
            "listening_services": [],
            "ip_forwarding": False,
            "tcp_syncookies": False,
            "icmp_redirects": True
        }
        
        # Check firewall status
        firewall_checks = [
            ("ufw", ["ufw", "status"]),
            ("iptables", ["iptables", "-L", "-n"]),
            ("firewalld", ["firewall-cmd", "--state"])
        ]
        
        for fw_name, cmd in firewall_checks:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    if fw_name == "ufw" and "Status: active" in result.stdout:
                        network_audit["firewall_status"] = "ufw_active"
                        self.passed_checks += 1
                    elif fw_name == "iptables" and "Chain" in result.stdout:
                        network_audit["firewall_status"] = "iptables_configured"
                        self.passed_checks += 1
                    elif fw_name == "firewalld" and "running" in result.stdout:
                        network_audit["firewall_status"] = "firewalld_active"
                        self.passed_checks += 1
            except Exception:
                pass
        
        self.total_checks += 1
        
        if network_audit["firewall_status"] == "unknown":
            self.audit_results["critical_issues"].append(
                "No firewall detected or firewall is not active"
            )
        
        # Check listening ports
        try:
            result = subprocess.run(['ss', '-tuln'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        state = parts[1]
                        local_addr = parts[4]
                        if state == "LISTEN":
                            network_audit["listening_services"].append(local_addr)
        except Exception:
            pass
        
        # Check kernel network parameters
        kernel_params = {
            "/proc/sys/net/ipv4/ip_forward": ("0", "ip_forwarding"),
            "/proc/sys/net/ipv4/tcp_syncookies": ("1", "tcp_syncookies"),
            "/proc/sys/net/ipv4/conf/all/accept_redirects": ("0", "icmp_redirects"),
            "/proc/sys/net/ipv4/conf/all/send_redirects": ("0", "icmp_send_redirects"),
            "/proc/sys/net/ipv4/conf/all/accept_source_route": ("0", "source_routing"),
            "/proc/sys/net/ipv4/icmp_echo_ignore_broadcasts": ("1", "ignore_broadcasts")
        }
        
        for param_file, (expected, name) in kernel_params.items():
            try:
                with open(param_file, 'r') as f:
                    value = f.read().strip()
                    if value == expected:
                        self.passed_checks += 1
                    else:
                        self.audit_results["misconfigurations"].append(
                            f"Kernel parameter {name} is not properly configured"
                        )
                self.total_checks += 1
            except Exception:
                pass
        
        return network_audit
    
    def check_ssh_configuration(self) -> Dict[str, Any]:
        """Audit SSH configuration"""
        ssh_audit = {
            "ssh_installed": False,
            "configuration": {},
            "host_keys": [],
            "issues": []
        }
        
        # Check if SSH is installed
        try:
            result = subprocess.run(['which', 'sshd'], capture_output=True)
            ssh_audit["ssh_installed"] = result.returncode == 0
        except Exception:
            pass
        
        if not ssh_audit["ssh_installed"]:
            return ssh_audit
        
        # Parse SSH configuration
        ssh_config_file = "/etc/ssh/sshd_config"
        recommended_settings = {
            "PermitRootLogin": "no",
            "PasswordAuthentication": "no",
            "PermitEmptyPasswords": "no",
            "X11Forwarding": "no",
            "MaxAuthTries": "3",
            "Protocol": "2",
            "StrictModes": "yes",
            "IgnoreRhosts": "yes",
            "HostbasedAuthentication": "no",
            "UsePAM": "yes"
        }
        
        try:
            with open(ssh_config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            key, value = parts
                            ssh_audit["configuration"][key] = value
        except Exception:
            ssh_audit["issues"].append("Unable to read SSH configuration")
        
        # Check recommended settings
        for setting, recommended in recommended_settings.items():
            actual = ssh_audit["configuration"].get(setting)
            if actual != recommended:
                if setting in ["PermitRootLogin", "PasswordAuthentication"]:
                    self.audit_results["critical_issues"].append(
                        f"SSH {setting} should be '{recommended}', found '{actual}'"
                    )
                else:
                    self.audit_results["misconfigurations"].append(
                        f"SSH {setting} should be '{recommended}', found '{actual}'"
                    )
            else:
                self.passed_checks += 1
            self.total_checks += 1
        
        # Check host keys
        host_key_files = [
            "/etc/ssh/ssh_host_rsa_key",
            "/etc/ssh/ssh_host_ecdsa_key",
            "/etc/ssh/ssh_host_ed25519_key"
        ]
        
        for key_file in host_key_files:
            if os.path.exists(key_file):
                stat_info = os.stat(key_file)
                perms = stat.S_IMODE(stat_info.st_mode)
                ssh_audit["host_keys"].append({
                    "file": key_file,
                    "permissions": oct(perms),
                    "secure": perms == 0o600
                })
                if perms != 0o600:
                    self.audit_results["vulnerabilities"].append(
                        f"SSH host key {key_file} has insecure permissions"
                    )
        
        return ssh_audit
    
    def check_system_updates(self) -> Dict[str, Any]:
        """Check system update status"""
        update_audit = {
            "package_manager": "unknown",
            "updates_available": 0,
            "security_updates": 0,
            "last_update": "unknown",
            "automatic_updates": False
        }
        
        # Detect package manager and check updates
        if os.path.exists('/usr/bin/apt'):
            update_audit["package_manager"] = "apt"
            try:
                # Update package list
                subprocess.run(['apt', 'update'], capture_output=True)
                
                # Check for updates
                result = subprocess.run(
                    ['apt', 'list', '--upgradable'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    updates = result.stdout.strip().split('\n')[1:]  # Skip header
                    update_audit["updates_available"] = len(updates)
                
                # Check for security updates
                result = subprocess.run(
                    ['apt', 'list', '--upgradable'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'security' in line:
                            update_audit["security_updates"] += 1
            except Exception:
                pass
            
            # Check unattended-upgrades
            if os.path.exists('/etc/apt/apt.conf.d/20auto-upgrades'):
                update_audit["automatic_updates"] = True
                self.passed_checks += 1
            else:
                self.audit_results["recommendations"].append(
                    "Enable automatic security updates with unattended-upgrades"
                )
            self.total_checks += 1
        
        elif os.path.exists('/usr/bin/yum'):
            update_audit["package_manager"] = "yum"
            # Similar checks for yum
        
        if update_audit["security_updates"] > 0:
            self.audit_results["critical_issues"].append(
                f"{update_audit['security_updates']} security updates available"
            )
        
        return update_audit
    
    def check_service_security(self) -> Dict[str, Any]:
        """Check security of running services"""
        service_audit = {
            "unnecessary_services": [],
            "vulnerable_services": [],
            "service_configurations": {}
        }
        
        # List of services that might be unnecessary
        potentially_unnecessary = [
            "telnet", "rsh", "rlogin", "tftp", "talk", "ntalk",
            "finger", "rexec", "rpc", "nis", "nfs"
        ]
        
        # Check running services
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--state=running'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    for service in potentially_unnecessary:
                        if service in line.lower():
                            service_audit["unnecessary_services"].append(service)
                            self.audit_results["misconfigurations"].append(
                                f"Potentially unnecessary service running: {service}"
                            )
        except Exception:
            pass
        
        # Check specific service configurations
        # Example: Check if MySQL is binding to all interfaces
        if os.path.exists('/etc/mysql/mysql.conf.d/mysqld.cnf'):
            try:
                with open('/etc/mysql/mysql.conf.d/mysqld.cnf', 'r') as f:
                    content = f.read()
                    if 'bind-address' not in content or 'bind-address = 0.0.0.0' in content:
                        service_audit["vulnerable_services"].append("mysql")
                        self.audit_results["vulnerabilities"].append(
                            "MySQL is potentially accessible from external networks"
                        )
            except Exception:
                pass
        
        return service_audit
    
    def check_logging_auditing(self) -> Dict[str, Any]:
        """Check logging and auditing configuration"""
        logging_audit = {
            "rsyslog_enabled": False,
            "auditd_enabled": False,
            "log_rotation": False,
            "important_logs": {}
        }
        
        # Check rsyslog
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'rsyslog'],
                capture_output=True, text=True
            )
            logging_audit["rsyslog_enabled"] = result.stdout.strip() == "active"
            if logging_audit["rsyslog_enabled"]:
                self.passed_checks += 1
            else:
                self.audit_results["misconfigurations"].append(
                    "System logging (rsyslog) is not active"
                )
        except Exception:
            pass
        self.total_checks += 1
        
        # Check auditd
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'auditd'],
                capture_output=True, text=True
            )
            logging_audit["auditd_enabled"] = result.stdout.strip() == "active"
            if not logging_audit["auditd_enabled"]:
                self.audit_results["recommendations"].append(
                    "Enable auditd for comprehensive system auditing"
                )
        except Exception:
            pass
        
        # Check log rotation
        logging_audit["log_rotation"] = os.path.exists('/etc/logrotate.conf')
        
        # Check important log files
        important_logs = [
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/kern.log",
            "/var/log/fail2ban.log"
        ]
        
        for log_file in important_logs:
            if os.path.exists(log_file):
                stat_info = os.stat(log_file)
                logging_audit["important_logs"][log_file] = {
                    "exists": True,
                    "size": stat_info.st_size,
                    "permissions": oct(stat.S_IMODE(stat_info.st_mode))
                }
        
        return logging_audit
    
    def generate_recommendations(self):
        """Generate security recommendations based on audit results"""
        # Priority recommendations based on findings
        if self.audit_results["security_score"] < 50:
            self.audit_results["recommendations"].insert(0,
                "URGENT: System security score is critically low. "
                "Immediate action required."
            )
        
        # Add general recommendations
        general_recommendations = [
            "Implement regular security updates and patch management",
            "Enable and configure host-based intrusion detection (AIDE/Tripwire)",
            "Implement centralized logging and monitoring",
            "Regular security audits and vulnerability scanning",
            "Implement network segmentation for services",
            "Use strong password policies and multi-factor authentication",
            "Regular backup and disaster recovery testing",
            "Implement security information and event management (SIEM)"
        ]
        
        # Add recommendations based on score
        if self.audit_results["security_score"] < 70:
            self.audit_results["recommendations"].extend(general_recommendations[:4])
        else:
            self.audit_results["recommendations"].extend(general_recommendations[-4:])
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete security audit"""
        print("Starting security audit...")
        
        # User account audit
        print("Auditing user accounts...")
        self.audit_results["user_accounts"] = self.check_user_accounts()
        
        # File permission audit
        print("Checking file permissions...")
        self.audit_results["file_permissions"] = self.check_file_permissions()
        
        # Network security audit
        print("Auditing network security...")
        self.audit_results["network_security"] = self.check_network_security()
        
        # SSH configuration audit
        print("Checking SSH configuration...")
        self.audit_results["ssh_security"] = self.check_ssh_configuration()
        
        # System updates audit
        print("Checking system updates...")
        self.audit_results["system_updates"] = self.check_system_updates()
        
        # Service security audit
        print("Auditing running services...")
        self.audit_results["service_security"] = self.check_service_security()
        
        # Logging and auditing check
        print("Checking logging configuration...")
        self.audit_results["logging_auditing"] = self.check_logging_auditing()
        
        # Calculate final score
        self.calculate_score()
        
        # Generate recommendations
        print("Generating recommendations...")
        self.generate_recommendations()
        
        # Summary
        self.audit_results["summary"] = {
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "critical_issues_count": len(self.audit_results["critical_issues"]),
            "vulnerabilities_count": len(self.audit_results["vulnerabilities"]),
            "misconfigurations_count": len(self.audit_results["misconfigurations"])
        }
        
        return self.audit_results


def main():
    """Main entry point"""
    auditor = SecurityAuditor()
    results = auditor.run_full_audit()
    
    # Output results as JSON
    print(json.dumps(results, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

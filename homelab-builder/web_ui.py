#!/usr/bin/env python3
"""
Homelab Builder Web Interface
Simple web UI for demonstrating the homelab builder functionality.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.environment_scanner import EnvironmentScanner
from agents.service_recommender import ServiceRecommender

class HomelabHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_index_html().encode())
        elif self.path == '/api/scan':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            scanner = EnvironmentScanner()
            scan_results = scanner.scan()
            self.wfile.write(json.dumps(scan_results).encode())
        elif self.path == '/api/services':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            recommender = ServiceRecommender()
            services = list(recommender.service_catalog.values())
            self.wfile.write(json.dumps(services).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_index_html(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homelab Builder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-12">
            <h1 class="text-5xl font-bold mb-4">
                <i class="fas fa-home text-blue-500"></i> Homelab Builder
            </h1>
            <p class="text-xl text-gray-400">Intelligent homelab installation made easy</p>
        </header>
        
        <div class="grid md:grid-cols-2 gap-8 mb-12">
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-semibold mb-4">
                    <i class="fas fa-server text-green-500"></i> System Information
                </h2>
                <div id="system-info" class="space-y-2">
                    <p class="text-gray-400">Loading system information...</p>
                </div>
            </div>
            
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-semibold mb-4">
                    <i class="fas fa-cogs text-purple-500"></i> Quick Actions
                </h2>
                <div class="space-y-3">
                    <button onclick="scanSystem()" class="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition">
                        <i class="fas fa-search"></i> Scan System
                    </button>
                    <button onclick="showServices()" class="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition">
                        <i class="fas fa-list"></i> View Available Services
                    </button>
                    <button onclick="startInstaller()" class="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded transition">
                        <i class="fas fa-rocket"></i> Start Installation
                    </button>
                </div>
            </div>
        </div>
        
        <div class="bg-gray-800 rounded-lg p-6 mb-8">
            <h2 class="text-2xl font-semibold mb-4">
                <i class="fas fa-box text-yellow-500"></i> Available Services
            </h2>
            <div id="services-list" class="grid md:grid-cols-3 gap-4">
                <p class="text-gray-400 col-span-3">Click "View Available Services" to load...</p>
            </div>
        </div>
        
        <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-2xl font-semibold mb-4">
                <i class="fas fa-terminal text-red-500"></i> Installation Output
            </h2>
            <div id="output" class="bg-black rounded p-4 font-mono text-sm h-64 overflow-y-auto">
                <p class="text-green-400">$ Ready to start installation...</p>
            </div>
        </div>
    </div>
    
    <script>
        async function scanSystem() {
            addOutput('Scanning system...');
            try {
                const response = await fetch('/api/scan');
                const data = await response.json();
                
                const systemInfo = document.getElementById('system-info');
                systemInfo.innerHTML = `
                    <p><i class="fas fa-microchip"></i> CPU Cores: <span class="text-blue-400">${data.cpu_count || 'Unknown'}</span></p>
                    <p><i class="fas fa-memory"></i> Memory: <span class="text-green-400">${data.memory?.total_gb?.toFixed(1) || '0'} GB</span></p>
                    <p><i class="fas fa-hdd"></i> Disk: <span class="text-yellow-400">${data.disk?.free_gb?.toFixed(1) || '0'} GB free</span></p>
                    <p><i class="fab fa-docker"></i> Docker: <span class="${data.docker?.installed ? 'text-green-400' : 'text-red-400'}">${data.docker?.installed ? 'Installed' : 'Not Installed'}</span></p>
                    <p><i class="fas fa-network-wired"></i> Network: <span class="text-purple-400">${data.network?.interfaces?.length || 0} interfaces</span></p>
                `;
                addOutput('System scan complete!');
            } catch (error) {
                addOutput('Error scanning system: ' + error.message, 'error');
            }
        }
        
        async function showServices() {
            addOutput('Loading available services...');
            try {
                const response = await fetch('/api/services');
                const services = await response.json();
                
                const servicesList = document.getElementById('services-list');
                servicesList.innerHTML = services.map(service => `
                    <div class="bg-gray-700 rounded p-4">
                        <h3 class="font-semibold text-lg mb-2">${service.name}</h3>
                        <p class="text-sm text-gray-400 mb-2">${service.purpose}</p>
                        <div class="text-xs space-y-1">
                            <p><i class="fas fa-microchip"></i> ${service.resources.cpu}</p>
                            <p><i class="fas fa-memory"></i> ${service.resources.memory}</p>
                            <p><i class="fas fa-signal"></i> ${service.difficulty}</p>
                        </div>
                    </div>
                `).join('');
                addOutput(`Loaded ${services.length} available services`);
            } catch (error) {
                addOutput('Error loading services: ' + error.message, 'error');
            }
        }
        
        function startInstaller() {
            addOutput('Starting interactive installer...');
            addOutput('Note: In production, this would launch the full installer');
            addOutput('Run ./install.sh from the terminal for the complete experience');
        }
        
        function addOutput(message, type = 'info') {
            const output = document.getElementById('output');
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? 'text-red-400' : 'text-green-400';
            output.innerHTML += `<p class="${color}">[${timestamp}] ${message}</p>`;
            output.scrollTop = output.scrollHeight;
        }
        
        // Load system info on page load
        window.onload = () => {
            scanSystem();
        };
    </script>
</body>
</html>"""

def run_server(port=8080):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, HomelabHandler)
    print(f"🌐 Homelab Builder Web UI running on http://0.0.0.0:{port}")
    print(f"📱 Access from browser at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local service=$1
    local port=$2
    echo -n "Checking $service (port $port): "
    if netstat -tuln | grep -q ":$port "; then
        echo -e "${GREEN}Running${NC}"
        return 0
    else
        echo -e "${RED}Not running${NC}"
        return 1
    fi
}

check_container() {
    local container=$1
    echo -n "Checking container $container: "
    if docker ps | grep -q "$container"; then
        echo -e "${GREEN}Running${NC}"
        return 0
    else
        echo -e "${RED}Not running${NC}"
        return 1
    fi
}

check_url() {
    local url=$1
    local name=$2
    echo -n "Checking $name at $url: "
    if curl -s -k -I "$url" | grep -q "HTTP/[1-2]"; then
        echo -e "${GREEN}Accessible${NC}"
        return 0
    else
        echo -e "${RED}Not accessible${NC}"
        return 1
    fi
}

# Header
echo "================================================"
echo "🔍 Homelab Deployment Verification"
echo "================================================"

# Check Docker
echo -e "\n📦 Checking Docker services..."
services=(
    "swag:443"
    "authelia:9091"
    "searxng:8080"
    "synapse:8008"
    "redis:6379"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    check_container "$name"
    check_service "$name" "$port"
done

# Check configurations
echo -e "\n📄 Checking configuration files..."
configs=(
    "/config/swag/nginx/proxy-confs/authelia.subdomain.conf"
    "/config/swag/nginx/proxy-confs/search.subdomain.conf"
    "/config/swag/nginx/proxy-confs/matrix.subdomain.conf"
    "/config/swag/nginx/authelia-location.conf"
    "/config/authelia/configuration.yml"
    "/config/authelia/users_database.yml"
    "/config/searxng/settings.yml"
    "/config/synapse/homeserver.yaml"
)

for config in "${configs[@]}"; do
    if [ -f "$config" ]; then
        echo -e "${GREEN}✓${NC} $config exists"
    else
        echo -e "${RED}✗${NC} $config missing"
    fi
done

# Check SSL certificates
echo -e "\n🔒 Checking SSL certificates..."
if [ -d "/config/swag/etc/letsencrypt/live" ]; then
    echo -e "${GREEN}✓${NC} SSL certificates directory exists"
    # Check certificate expiration
    cert_file=$(find /config/swag/etc/letsencrypt/live -name cert.pem | head -n 1)
    if [ -n "$cert_file" ]; then
        expiry=$(openssl x509 -enddate -noout -in "$cert_file" | cut -d= -f2)
        echo "Certificate expires: $expiry"
    fi
else
    echo -e "${RED}✗${NC} SSL certificates directory missing"
fi

# Check network connectivity
echo -e "\n🌐 Checking network connectivity..."
if [ -n "$DOMAIN" ]; then
    urls=(
        "https://authelia.$DOMAIN"
        "https://search.$DOMAIN"
        "https://matrix.$DOMAIN"
    )
    for url in "${urls[@]}"; do
        check_url "$url" "$(echo "$url" | cut -d. -f1)"
    done
else
    echo -e "${YELLOW}⚠${NC} DOMAIN environment variable not set"
fi

# Check logs for errors
echo -e "\n📝 Checking for errors in logs..."
for service in swag authelia searxng synapse redis; do
    echo "Last 5 errors from $service:"
    docker logs "$service" 2>&1 | grep -i "error" | tail -n 5
done

echo -e "\n================================================"
echo "Verification complete!"
echo "================================================"

# Provide helpful information
echo -e "\n📋 Next steps:"
echo "1. Check any failed services above"
echo "2. Review logs with: docker logs <container-name>"
echo "3. Verify Authelia authentication is working"
echo "4. Test Matrix federation if enabled"
echo "5. Confirm SearXNG search functionality"

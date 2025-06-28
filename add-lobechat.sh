#!/bin/bash

# LobeChat Integration Script for Paradelala Homelab-Alt
# This script adds LobeChat to an existing Paradelala installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Check if we're in the Paradelala directory
if [ ! -f "docker-compose.yml" ] || [ ! -f ".env" ]; then
    print_error "This script must be run from the Paradelala homelab-alt directory"
    print_error "Please cd to your Paradelala installation directory first"
    exit 1
fi

# Check if docker-compose is running
if ! docker compose ps >/dev/null 2>&1; then
    print_warning "Docker Compose doesn't appear to be running. Make sure Paradelala is installed first."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

print_section "LobeChat Integration for Paradelala"
print_info "This script will add LobeChat with database support to your Paradelala setup"

# Backup existing files
print_section "Creating Backups"
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)
cp .env .env.backup-$(date +%Y%m%d-%H%M%S)
print_info "Backups created"

# Generate secure passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

print_section "Generating Secure Keys"
LOBE_POSTGRES_PASSWORD=$(generate_password)
LOBE_MINIO_PASSWORD=$(generate_password)
LOBE_AUTH_SECRET=$(generate_password)
LOBE_KEY_VAULTS_SECRET=$(generate_password)

# Add environment variables to .env
print_section "Adding Environment Variables"
cat >> .env << EOF

# ===========================
# LobeChat Configuration
# ===========================
# Generated on $(date)

# Database
LOBE_POSTGRES_PASSWORD=${LOBE_POSTGRES_PASSWORD}

# MinIO S3 Storage
LOBE_MINIO_USER=admin
LOBE_MINIO_PASSWORD=${LOBE_MINIO_PASSWORD}

# Security Keys
LOBE_AUTH_SECRET=${LOBE_AUTH_SECRET}
LOBE_KEY_VAULTS_SECRET=${LOBE_KEY_VAULTS_SECRET}

# Casdoor Authentication
LOBE_CASDOOR_ID=a387a4892ee19b1a2249
LOBE_CASDOOR_SECRET=dbf205949d704de81b0b5b3603174e23fbecc354

# AI Provider Keys (Add your own)
# OPENAI_API_KEY=sk-xxxx
# ANTHROPIC_API_KEY=sk-ant-xxxx
# GOOGLE_API_KEY=xxxx
# GROQ_API_KEY=gsk_xxxx
# DEEPSEEK_API_KEY=sk-xxxx
EOF

print_info "Environment variables added to .env"

# Create directory structure
print_section "Creating Directory Structure"
mkdir -p lobe-data/postgres
mkdir -p lobe-data/s3
mkdir -p lobe-data/casdoor
print_info "Directories created"

# Download and configure Casdoor init data
print_section "Configuring Casdoor"
print_info "Downloading Casdoor initialization data..."
curl -fsSL https://raw.githubusercontent.com/lobehub/lobe-chat/HEAD/docker-compose/local/init_data.json -o lobe-data/casdoor/init_data.json

# Get domain from .env
DOMAIN=$(grep "^DOMAIN=" .env | cut -d'=' -f2)
if [ -z "$DOMAIN" ]; then
    print_error "DOMAIN not found in .env file"
    exit 1
fi

print_info "Configuring for domain: $DOMAIN"
sed -i "s|http://localhost:3210|https://lobe.${DOMAIN}|g" lobe-data/casdoor/init_data.json
sed -i "s|http://localhost:8000|https://auth.${DOMAIN}|g" lobe-data/casdoor/init_data.json

# Create a temporary file for the services to add
print_section "Adding LobeChat Services to docker-compose.yml"
cat > lobechat-services.yml << 'EOF'

  # ===========================
  # LobeChat Services
  # ===========================
  
  # PostgreSQL with pgvector for LobeChat
  lobe-postgres:
    image: pgvector/pgvector:pg17
    container_name: lobe-postgres
    volumes:
      - './lobe-data/postgres:/var/lib/postgresql/data'
    environment:
      - 'POSTGRES_DB=lobechat'
      - 'POSTGRES_PASSWORD=${LOBE_POSTGRES_PASSWORD}'
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U postgres']
      interval: 5s
      timeout: 5s
      retries: 5
    restart: always
    networks:
      - web

  # MinIO S3 Storage for LobeChat
  lobe-minio:
    image: minio/minio
    container_name: lobe-minio
    volumes:
      - './lobe-data/s3:/data'
    environment:
      - 'MINIO_ROOT_USER=${LOBE_MINIO_USER}'
      - 'MINIO_ROOT_PASSWORD=${LOBE_MINIO_PASSWORD}'
      - 'MINIO_BROWSER_REDIRECT_URL=https://minio.${DOMAIN}'
      - 'MINIO_API_CORS_ALLOW_ORIGIN=*'
    command: server /data --console-address ":9001"
    restart: always
    networks:
      - web
    labels:
      - "traefik.enable=true"
      # MinIO S3 API
      - "traefik.http.routers.minio-api.rule=Host(`s3.${DOMAIN}`)"
      - "traefik.http.routers.minio-api.entrypoints=websecure"
      - "traefik.http.routers.minio-api.tls.certresolver=letsencrypt"
      - "traefik.http.services.minio-api.loadbalancer.server.port=9000"
      # MinIO Console
      - "traefik.http.routers.minio-console.rule=Host(`minio.${DOMAIN}`)"
      - "traefik.http.routers.minio-console.entrypoints=websecure"
      - "traefik.http.routers.minio-console.tls.certresolver=letsencrypt"
      - "traefik.http.services.minio-console.loadbalancer.server.port=9001"

  # Casdoor Authentication for LobeChat
  lobe-casdoor:
    image: casbin/casdoor:v1.843.0
    container_name: lobe-casdoor
    depends_on:
      lobe-postgres:
        condition: service_healthy
    environment:
      driverName: 'postgres'
      dataSourceName: 'user=postgres password=${LOBE_POSTGRES_PASSWORD} host=lobe-postgres port=5432 sslmode=disable dbname=casdoor'
      httpport: '8000'
      origin: 'https://auth.${DOMAIN}'
      runmode: 'prod'
    volumes:
      - ./lobe-data/casdoor/init_data.json:/init_data.json
    restart: always
    networks:
      - web
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.casdoor.rule=Host(`auth.${DOMAIN}`)"
      - "traefik.http.routers.casdoor.entrypoints=websecure"
      - "traefik.http.routers.casdoor.tls.certresolver=letsencrypt"
      - "traefik.http.services.casdoor.loadbalancer.server.port=8000"
    entrypoint: /bin/sh -c './server --createDatabase=true'

  # LobeChat Application
  lobechat:
    image: lobehub/lobe-chat-database:latest
    container_name: lobechat
    depends_on:
      lobe-postgres:
        condition: service_healthy
      lobe-minio:
        condition: service_started
      lobe-casdoor:
        condition: service_started
    environment:
      # Core Configuration
      - 'APP_URL=https://lobe.${DOMAIN}'
      - 'NEXT_AUTH_SECRET=${LOBE_AUTH_SECRET}'
      - 'KEY_VAULTS_SECRET=${LOBE_KEY_VAULTS_SECRET}'
      
      # Database
      - 'DATABASE_URL=postgresql://postgres:${LOBE_POSTGRES_PASSWORD}@lobe-postgres:5432/lobechat'
      
      # Authentication
      - 'NEXT_AUTH_SSO_PROVIDERS=casdoor'
      - 'AUTH_URL=https://lobe.${DOMAIN}/api/auth'
      - 'NEXTAUTH_URL=https://lobe.${DOMAIN}/api/auth'
      - 'AUTH_CASDOOR_ISSUER=https://auth.${DOMAIN}'
      - 'AUTH_CASDOOR_ID=${LOBE_CASDOOR_ID}'
      - 'AUTH_CASDOOR_SECRET=${LOBE_CASDOOR_SECRET}'
      
      # S3 Storage
      - 'S3_ENDPOINT=https://s3.${DOMAIN}'
      - 'S3_PUBLIC_DOMAIN=https://s3.${DOMAIN}'
      - 'S3_BUCKET=lobe'
      - 'S3_ACCESS_KEY_ID=${LOBE_MINIO_USER}'
      - 'S3_SECRET_ACCESS_KEY=${LOBE_MINIO_PASSWORD}'
      - 'S3_ENABLE_PATH_STYLE=1'
      - 'S3_SET_ACL=0'
      - 'LLM_VISION_IMAGE_USE_BASE64=1'
      
      # AI Providers (configured in .env)
      - 'OPENAI_API_KEY=${OPENAI_API_KEY:-}'
      - 'ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}'
      - 'GOOGLE_API_KEY=${GOOGLE_API_KEY:-}'
      - 'GROQ_API_KEY=${GROQ_API_KEY:-}'
      - 'DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-}'
    restart: always
    networks:
      - web
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.lobechat.rule=Host(`lobe.${DOMAIN}`)"
      - "traefik.http.routers.lobechat.entrypoints=websecure"
      - "traefik.http.routers.lobechat.tls.certresolver=letsencrypt"
      - "traefik.http.services.lobechat.loadbalancer.server.port=3210"
      # Security headers
      - "traefik.http.middlewares.lobechat-headers.headers.stsSeconds=31536000"
      - "traefik.http.middlewares.lobechat-headers.headers.stsIncludeSubdomains=true"
      - "traefik.http.middlewares.lobechat-headers.headers.forceSTSHeader=true"
      - "traefik.http.routers.lobechat.middlewares=lobechat-headers"
EOF

# Append services to docker-compose.yml
# Remove the last line (which should be empty or just whitespace) to ensure clean append
sed -i '$ d' docker-compose.yml 2>/dev/null || true
cat lobechat-services.yml >> docker-compose.yml
rm lobechat-services.yml

print_info "Services added to docker-compose.yml"

# Create MinIO bucket initialization script
print_section "Creating MinIO Initialization Script"
cat > init-lobechat-minio.sh << 'EOF'
#!/bin/bash
# Initialize MinIO bucket for LobeChat

echo "Waiting for MinIO to be ready..."
sleep 10

# Create alias and bucket
docker exec lobe-minio mc alias set myminio http://localhost:9000 ${LOBE_MINIO_USER} ${LOBE_MINIO_PASSWORD}
docker exec lobe-minio mc mb myminio/lobe --ignore-existing
docker exec lobe-minio mc anonymous set public myminio/lobe

echo "MinIO bucket 'lobe' created and configured"
EOF

chmod +x init-lobechat-minio.sh

# Create update script
print_section "Creating Update Script"
cat > update-lobechat.sh << 'EOF'
#!/bin/bash
# Update LobeChat and related services

echo "Updating LobeChat services..."
docker compose pull lobechat lobe-casdoor lobe-minio lobe-postgres
docker compose up -d lobechat lobe-casdoor lobe-minio lobe-postgres
echo "LobeChat services updated"
EOF

chmod +x update-lobechat.sh

# Create migration script for existing LobeChat data
print_section "Creating Migration Script"
cat > migrate-lobechat-data.sh << 'EOF'
#!/bin/bash
# Migrate data from standalone LobeChat to Paradelala integration

STANDALONE_DIR="$HOME/lobe-chat-db"

if [ ! -d "$STANDALONE_DIR" ]; then
    echo "No standalone LobeChat installation found at $STANDALONE_DIR"
    exit 0
fi

echo "Found standalone LobeChat installation"
read -p "Migrate data from standalone installation? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Stop standalone LobeChat
    echo "Stopping standalone LobeChat..."
    cd "$STANDALONE_DIR"
    docker compose down
    
    # Go back to Paradelala directory
    cd - > /dev/null
    
    # Copy data
    echo "Copying PostgreSQL data..."
    if [ -d "$STANDALONE_DIR/data" ]; then
        cp -r "$STANDALONE_DIR/data/"* ./lobe-data/postgres/ 2>/dev/null || true
    fi
    
    echo "Copying MinIO/S3 data..."
    if [ -d "$STANDALONE_DIR/s3_data" ]; then
        cp -r "$STANDALONE_DIR/s3_data/"* ./lobe-data/s3/ 2>/dev/null || true
    fi
    
    echo "Migration complete!"
    echo "You can remove the old installation with: rm -rf $STANDALONE_DIR"
fi
EOF

chmod +x migrate-lobechat-data.sh

print_section "Installation Summary"
print_info "LobeChat integration complete!"
echo
print_info "Next steps:"
echo "1. Review the changes in docker-compose.yml and .env"
echo "2. Add your AI provider API keys to .env file"
echo "3. Start LobeChat services:"
echo "   docker compose up -d"
echo "4. Wait 30 seconds, then initialize MinIO:"
echo "   ./init-lobechat-minio.sh"
echo "5. Check logs:"
echo "   docker compose logs -f lobechat"
echo
print_info "LobeChat will be available at:"
echo "   - LobeChat: https://lobe.${DOMAIN}"
echo "   - Casdoor Admin: https://auth.${DOMAIN}"
echo "   - MinIO Console: https://minio.${DOMAIN}"
echo "   - S3 API: https://s3.${DOMAIN}"
echo
print_info "To migrate data from standalone LobeChat:"
echo "   ./migrate-lobechat-data.sh"
echo
print_warning "Remember to configure your AI provider API keys in .env!"

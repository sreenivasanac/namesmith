# Deployment Instructions - Hetzner VPS with Docker

This guide covers deploying Namesmith to a Hetzner VPS using a fully containerized approach with Docker Compose, Nginx, and automatic SSL certificates.

## Prerequisites

1. **Hetzner VPS** with:
   - Ubuntu 24.04 or similar
   - Minimum 2GB RAM, 2 vCPUs
   - Docker and Docker Compose installed
   
2. **Domain DNS** configured:
   - A record pointing to your VPS IP address
   - Example: `namesmith.pragnyalabs.com` → `your.vps.ip.address`

3. **API Keys** ready:
   - OpenAI API key
   - WhoAPI API key
   - WhoisJSON API key

## Step 1: Prepare Your VPS

```bash
# SSH into your Hetzner VPS
ssh root@your-vps-ip

# Update system packages
apt update && apt upgrade -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose-plugin -y

# Verify Docker installation
docker --version
docker compose version

# Create deployment directory
mkdir -p /opt/namesmith
cd /opt/namesmith
```

## Step 2: Upload Project Files

From your local machine:

```bash
# Navigate to project root
cd /Users/sreenivasanac/SoftwareProjects/namesmith

# Upload to VPS (excluding development files)
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude '__pycache__' \
  --exclude '*.pyc' --exclude '.next' --exclude '.git' \
  ./ root@your-vps-ip:/opt/namesmith/
```

## Step 3: Configure Environment

```bash
# SSH back into your VPS
ssh root@your-vps-ip
cd /opt/namesmith/deploy

# Copy and edit environment file
cp app.env.example app.env
nano app.env
```

Edit `app.env` with your actual values:

```env
# Domain configuration
DOMAIN=namesmith.pragnyalabs.com

# Database (set a strong password)
POSTGRES_DB=namesmith_db
POSTGRES_USER=namesmith_admin
POSTGRES_PASSWORD=your-strong-password-here

# API configuration
DATABASE_URL=postgresql+asyncpg://namesmith_admin:<same-password-as-above>@db:5432/namesmith_db
OPENAI_API_KEY=<your-openai-api-key>
WHOISJSON_API_KEY=<your-whoisjson-api-key>
WHOAPI_API_KEY=<your-whoapi-api-key>

# Background workers
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Frontend API URL (must match your domain)
NEXT_PUBLIC_API_URL=https://namesmith.pragnyalabs.com/api
```

## Step 4: Obtain SSL Certificate (First Time Only)

Before starting all services, obtain SSL certificate:

```bash
cd /opt/namesmith

# Start nginx temporarily without SSL
docker compose -f deploy/docker-compose.yaml up -d nginx

# Obtain certificate
docker compose -f deploy/docker-compose.yaml run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  -d namesmith.pragnyalabs.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# Restart nginx to load certificates
docker compose -f deploy/docker-compose.yaml restart nginx
```

## Step 5: Start All Services

```bash
cd /opt/namesmith

# Build and start all services
docker compose -f deploy/docker-compose.yaml up -d --build

# This will start:
# - PostgreSQL database
# - Redis cache
# - API backend (Python/FastAPI)
# - Web frontend (Next.js)
# - Nginx reverse proxy
# - Certbot for SSL renewal
```

## Step 6: Verify Deployment

```bash
# Check all containers are running
docker compose -f deploy/docker-compose.yaml ps

# Should show all services as "Up" or "running"

# Check logs
docker compose -f deploy/docker-compose.yaml logs -f

# Check specific service logs
docker compose -f deploy/docker-compose.yaml logs api
docker compose -f deploy/docker-compose.yaml logs web
docker compose -f deploy/docker-compose.yaml logs nginx

# Test API endpoint
curl https://namesmith.pragnyalabs.com/api/health

# Access web interface
# Open browser: https://namesmith.pragnyalabs.com
```

## Management Commands

### View Logs
```bash
cd /opt/namesmith

# All services
docker compose -f deploy/docker-compose.yaml logs -f

# Specific service
docker compose -f deploy/docker-compose.yaml logs -f api
docker compose -f deploy/docker-compose.yaml logs -f web
docker compose -f deploy/docker-compose.yaml logs -f nginx
```

### Restart Services
```bash
cd /opt/namesmith

# Restart all
docker compose -f deploy/docker-compose.yaml restart

# Restart specific service
docker compose -f deploy/docker-compose.yaml restart api
docker compose -f deploy/docker-compose.yaml restart web
```

### Stop Services
```bash
cd /opt/namesmith
docker compose -f deploy/docker-compose.yaml down
```

### Update Application
```bash
cd /opt/namesmith

# Pull latest code (if using git)
git pull

# Or upload new files via rsync
# From local: rsync -avz ... root@your-vps-ip:/opt/namesmith/

# Rebuild and restart
docker compose -f deploy/docker-compose.yaml down
docker compose -f deploy/docker-compose.yaml up -d --build
```

### Database Backup
```bash
# Backup database
docker compose -f /opt/namesmith/deploy/docker-compose.yaml exec db \
  pg_dump -U namesmith_admin namesmith_db > backup-$(date +%Y%m%d).sql

# Restore database
cat backup-20251025.sql | docker compose -f /opt/namesmith/deploy/docker-compose.yaml exec -T db \
  psql -U namesmith_admin namesmith_db
```

### View Database
```bash
# Connect to PostgreSQL
docker compose -f /opt/namesmith/deploy/docker-compose.yaml exec db \
  psql -U namesmith_admin namesmith_db
```

## Troubleshooting

### SSL Certificate Issues
```bash
# Check certificate status
docker compose -f deploy/docker-compose.yaml exec nginx \
  ls -la /etc/letsencrypt/live/

# Manually renew certificate
docker compose -f deploy/docker-compose.yaml run --rm certbot renew

# Check nginx config
docker compose -f deploy/docker-compose.yaml exec nginx nginx -t
```

### Container Not Starting
```bash
# Check logs
docker compose -f deploy/docker-compose.yaml logs [service-name]

# Check resources
docker stats

# Restart specific service
docker compose -f deploy/docker-compose.yaml restart [service-name]
```

### Database Connection Issues
```bash
# Check if database is running
docker compose -f deploy/docker-compose.yaml ps db

# Check database logs
docker compose -f deploy/docker-compose.yaml logs db

# Verify DATABASE_URL in app.env matches credentials
```

### Port Already in Use
```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting service
sudo systemctl stop nginx  # if system nginx is running
```

## Security Recommendations

1. **Firewall**: Configure UFW
   ```bash
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

2. **Regular Updates**: Keep system and Docker images updated
   ```bash
   apt update && apt upgrade -y
   docker compose -f deploy/docker-compose.yaml pull
   docker compose -f deploy/docker-compose.yaml up -d
   ```

3. **Backup**: Schedule regular database backups (use cron)

4. **Monitoring**: Consider adding monitoring (e.g., Prometheus, Grafana)

## Architecture

```
Internet
   ↓
Nginx (Port 80/443) - SSL Termination
   ↓
   ├→ /api → API Service (FastAPI)
   │         ↓
   │         Database (PostgreSQL)
   │         Redis
   └→ / → Web Service (Next.js)
```

All services run in isolated Docker containers on the same network (`namesmith-network`).

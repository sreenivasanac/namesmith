# Post-Deployment Steps for Namesmith

## Current Deployment Status ✅

Your Namesmith application is now successfully deployed and running on your Hetzner VPS at **65.108.149.90**!

### What's Working:
- ✅ All Docker containers are running (API, Web, Database, Redis, Nginx)
- ✅ API is accessible at: `http://65.108.149.90/api/`
- ✅ Web frontend is accessible at: `http://65.108.149.90/`
- ✅ Database migrations completed successfully
- ✅ Health endpoints responding correctly

### Test Your Deployment:
```bash
# Test API
curl http://65.108.149.90/api/
# Expected: {"service":"Namesmith","status":"ok"}

# Test Health Endpoint
curl http://65.108.149.90/api/healthz
# Expected: {"status":"ok"}

# Test Web Frontend (should redirect to /login)
curl -I http://65.108.149.90/
```

## Next Steps: DNS and SSL Setup

To access your application via `https://namesmith.pragnyalabs.com`, follow these steps:

### Step 1: Configure DNS

Add an A record to your domain's DNS settings:

```
Type: A
Name: namesmith (or @ for root domain)
Value: 65.108.149.90
TTL: 3600 (or Auto)
```

**Where to configure:**
- If using Cloudflare: DNS > Records
- If using your domain registrar: DNS Management section
- If using another DNS provider: Consult their documentation

**Verify DNS is working:**
```bash
nslookup namesmith.pragnyalabs.com
# Should return: 65.108.149.90
```

### Step 2: Obtain SSL Certificate

Once DNS is configured and propagated (usually 5-60 minutes), run:

```bash
cd /home/sreenivasanac/projects/namesmith

# Stop all services
docker compose -f deploy/docker-compose.yaml down

# Update nginx to use HTTPS configuration
cd deploy
cp nginx.conf nginx.conf.backup
# (nginx.conf already has HTTPS configuration)

# Update docker-compose to use the HTTPS nginx config
sed -i 's/nginx-http-only.conf/nginx.conf/' docker-compose.yaml

# Start services
docker compose -f docker-compose.yaml up -d

# Obtain SSL certificate
docker compose -f docker-compose.yaml run --rm certbot certonly \\
  --webroot --webroot-path /var/www/certbot \\
  -d namesmith.pragnyalabs.com \\
  --email sreenivasanac@gmail.com \\
  --agree-tos \\
  --no-eff-email

# Restart nginx to load certificates
docker compose -f docker-compose.yaml restart nginx
```

### Step 3: Verify HTTPS

```bash
# Test HTTPS endpoint
curl https://namesmith.pragnyalabs.com/api/
# Expected: {"service":"Namesmith","status":"ok"}

# Open in browser
# Visit: https://namesmith.pragnyalabs.com
```

## SSL Certificate Renewal

Certbot will automatically attempt to renew certificates. The renewal process runs every 12 hours via the certbot container.

To manually renew:
```bash
cd /home/sreenivasanac/projects/namesmith
docker compose -f deploy/docker-compose.yaml run --rm certbot renew
docker compose -f deploy/docker-compose.yaml restart nginx
```

## Troubleshooting

### DNS Not Resolving
- Wait 5-60 minutes for DNS propagation
- Check DNS with: `dig namesmith.pragnyalabs.com +short`
- Verify A record is correctly set in your DNS provider

### SSL Certificate Error
- Ensure DNS is fully propagated before obtaining certificate
- Check nginx logs: `docker compose -f deploy/docker-compose.yaml logs nginx`
- Verify port 80 is accessible externally (needed for certificate validation)

### API Not Responding
- Check API logs: `docker compose -f deploy/docker-compose.yaml logs api`
- Verify database connection: `docker compose -f deploy/docker-compose.yaml ps`
- Restart API: `docker compose -f deploy/docker-compose.yaml restart api`

## Management Commands

### View Logs
```bash
cd /home/sreenivasanac/projects/namesmith

# All services
docker compose -f deploy/docker-compose.yaml logs -f

# Specific service
docker compose -f deploy/docker-compose.yaml logs -f api
docker compose -f deploy/docker-compose.yaml logs -f web
docker compose -f deploy/docker-compose.yaml logs -f nginx
```

### Restart Services
```bash
# Restart all
docker compose -f deploy/docker-compose.yaml restart

# Restart specific service
docker compose -f deploy/docker-compose.yaml restart api
```

### Update Application
```bash
cd /home/sreenivasanac/projects/namesmith

# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker compose -f deploy/docker-compose.yaml down
docker compose -f deploy/docker-compose.yaml up -d --build
```

## Security Recommendations

1. **Configure Firewall:**
   ```bash
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

2. **Change Database Password:**
   The current password is `Namesmith2025Pass`. To change it:
   ```bash
   docker compose -f deploy/docker-compose.yaml exec db \\
     psql -U namesmith_admin -d namesmith_db \\
     -c "ALTER USER namesmith_admin WITH PASSWORD 'your-new-strong-password';"
   
   # Update deploy/app.env with the new password
   # Then restart: docker compose -f deploy/docker-compose.yaml restart api
   ```

3. **Regular Backups:**
   ```bash
   # Backup database
   docker compose -f deploy/docker-compose.yaml exec db \\
     pg_dump -U namesmith_admin namesmith_db > backup-$(date +%Y%m%d).sql
   ```

4. **Monitor Resources:**
   ```bash
   # Check container resource usage
   docker stats
   
   # Check system resources
   htop  # or top
   df -h  # disk usage
   ```

## Environment Configuration

Key environment variables in `/home/sreenivasanac/projects/namesmith/deploy/app.env`:

- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `WHOAPI_API_KEY`: WhoAPI key for domain lookups
- `WHOISJSON_API_KEY`: WhoisJSON key for domain information
- `NEXT_PUBLIC_API_URL`: Frontend API URL (update to HTTPS after SSL)

After DNS and SSL setup, update `NEXT_PUBLIC_API_URL` in `app.env`:
```
NEXT_PUBLIC_API_URL=https://namesmith.pragnyalabs.com/api
```

Then rebuild the web container:
```bash
docker compose -f deploy/docker-compose.yaml up -d --build web
```

## Support

For issues or questions, refer to:
- Main README: `/home/sreenivasanac/projects/namesmith/README.md`
- Deployment Guide: `/home/sreenivasanac/projects/namesmith/deploy/DEPLOYMENT.md`

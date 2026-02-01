# Nilam Bangladesh - Production Deployment Guide
## Domain: nilambd.com

## 📋 Pre-Deployment Checklist

### 1. Domain & DNS Configuration
- [ ] Purchase domain: nilambd.com (already owned)
- [ ] Configure DNS records:
  ```
  A Record:     nilambd.com → Your_Server_IP
  A Record:     www.nilambd.com → Your_Server_IP
  CNAME Record: api.nilambd.com → Your_Server_IP
  ```
- [ ] Set up SSL certificates (Let's Encrypt recommended)

### 2. Required API Keys & Credentials

#### bKash Production Credentials
**Where to get:**
1. Visit: https://developer.bka.sh/
2. Apply for merchant account
3. Complete KYC verification
4. Obtain production credentials:
   - Username
   - Password  
   - App Key
   - App Secret

**Update in:** `/app/backend/.env.production`

#### MongoDB Atlas (Production Database)
**Setup:**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create new cluster (Free M0 tier available)
3. Whitelist your server IP
4. Create database user
5. Get connection string

**Update in:** `/app/backend/.env.production` → `MONGO_URL`

#### Google OAuth (Sign in with Google)
**Setup:**
1. Go to: https://console.cloud.google.com/
2. Create new project: "Nilam Bangladesh"
3. Enable Google+ API
4. Go to: APIs & Services → Credentials
5. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized JavaScript origins: 
     - https://nilambd.com
     - https://www.nilambd.com
   - Authorized redirect URIs:
     - https://nilambd.com/auth/google/callback
     - https://api.nilambd.com/api/auth/google/callback

**Update in:**
- Backend: `/app/backend/.env.production` → `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- Frontend: `/app/frontend/.env.production` → `REACT_APP_GOOGLE_CLIENT_ID`

#### Firebase (Phone Authentication)
**Setup:**
1. Go to: https://console.firebase.google.com/
2. Create new project: "Nilam Bangladesh"
3. Add web app to project
4. Enable Authentication → Phone
5. Add authorized domains:
   - nilambd.com
   - www.nilambd.com
6. Copy config values from Project Settings

**Update in:** `/app/frontend/.env.production` → All `REACT_APP_FIREBASE_*` variables

#### Supabase Real-Time Setup
**Already configured!** Just need to create tables:

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Go to: SQL Editor
4. Run this script:

```sql
-- Create bids table for real-time sync
CREATE TABLE IF NOT EXISTS public.bids (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  listing_id TEXT NOT NULL,
  bidder_id TEXT NOT NULL,
  bidder_username TEXT NOT NULL,
  amount NUMERIC NOT NULL,
  is_proxy_bid BOOLEAN DEFAULT FALSE,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_bids_listing_id ON public.bids(listing_id);
CREATE INDEX IF NOT EXISTS idx_bids_timestamp ON public.bids(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_bids_bidder_id ON public.bids(bidder_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.bids ENABLE ROW LEVEL SECURITY;

-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to all users" ON public.bids
  FOR SELECT
  USING (true);

-- Enable real-time
ALTER PUBLICATION supabase_realtime ADD TABLE public.bids;

-- Verify real-time is enabled
SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
```

### 3. Server Setup (Ubuntu/Debian)

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.10+
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install MongoDB (or use MongoDB Atlas)
# If using Atlas, skip this step

# Install Nginx
sudo apt install -y nginx

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

#### Clone & Setup Application
```bash
# Clone repository
cd /var/www
git clone YOUR_REPO_URL nilam
cd nilam

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.production .env
# Edit .env with production values
nano .env

# Frontend setup
cd ../frontend
npm install
cp .env.production .env
# Edit .env with production values
nano .env
npm run build
```

#### Configure Nginx
Create `/etc/nginx/sites-available/nilambd.com`:

```nginx
# Frontend - nilambd.com
server {
    listen 80;
    server_name nilambd.com www.nilambd.com;

    root /var/www/nilam/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# Backend API - api.nilambd.com
server {
    listen 80;
    server_name api.nilambd.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/nilambd.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Setup SSL Certificates
```bash
sudo certbot --nginx -d nilambd.com -d www.nilambd.com -d api.nilambd.com
```

#### Create Systemd Service for Backend
Create `/etc/systemd/system/nilam-backend.service`:

```ini
[Unit]
Description=Nilam Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/nilam/backend
Environment="PATH=/var/www/nilam/backend/venv/bin"
ExecStart=/var/www/nilam/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nilam-backend
sudo systemctl start nilam-backend
sudo systemctl status nilam-backend
```

### 4. Security Configuration

#### Firewall Setup
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

#### MongoDB Security (if self-hosted)
```bash
# Enable authentication
sudo nano /etc/mongod.conf

# Add:
security:
  authorization: enabled

# Restart
sudo systemctl restart mongod
```

### 5. Monitoring & Logs

#### View Backend Logs
```bash
sudo journalctl -u nilam-backend -f
```

#### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### Setup Auto-Restart
Backend service already configured with `Restart=always`

### 6. Testing Production

1. **Test Website:**
   - Visit: https://nilambd.com
   - Check: SSL certificate (should show green padlock)
   - Test: Registration, login, browsing

2. **Test API:**
   - Visit: https://api.nilambd.com/api/
   - Should return: `{"message": "Nilam API"}`

3. **Test bKash Payment:**
   - Create test listing
   - Attempt payment
   - Verify callback handling

4. **Test Real-Time Bids:**
   - Open two browser windows
   - Place bid in one
   - Verify updates in other

### 7. Backup Strategy

#### Database Backup (Daily)
```bash
# Create backup script
nano /usr/local/bin/backup-nilam-db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/nilam"
mkdir -p $BACKUP_DIR

# MongoDB backup
mongodump --uri="YOUR_MONGODB_URI" --out="$BACKUP_DIR/db_$DATE"

# Keep last 7 days only
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +
```

Make executable and add to crontab:
```bash
chmod +x /usr/local/bin/backup-nilam-db.sh
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-nilam-db.sh
```

## 🚀 Go Live Steps

1. ✅ Complete all items in Pre-Deployment Checklist
2. ✅ Test all features in staging environment
3. ✅ Run production build: `npm run build`
4. ✅ Deploy to server
5. ✅ Configure DNS
6. ✅ Setup SSL
7. ✅ Start backend service
8. ✅ Test thoroughly
9. ✅ Monitor logs for 24 hours
10. ✅ Announce launch! 🎉

## 📞 Support

For issues during deployment:
- Check logs: `sudo journalctl -u nilam-backend -f`
- Verify environment variables
- Test API endpoints individually
- Check Nginx configuration

## 🔄 Updates & Maintenance

### Deploy New Version
```bash
cd /var/www/nilam
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nilam-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

### Monitor System Health
```bash
# Check services
sudo systemctl status nilam-backend
sudo systemctl status nginx
sudo systemctl status mongod  # if self-hosted

# Check disk space
df -h

# Check memory
free -h
```

## ✅ Production Checklist Summary

- [ ] Domain DNS configured
- [ ] SSL certificates installed
- [ ] MongoDB production database setup
- [ ] All API keys configured
- [ ] bKash production credentials added
- [ ] Google OAuth configured
- [ ] Firebase phone auth setup
- [ ] Supabase tables created
- [ ] Nginx configured and running
- [ ] Backend service running
- [ ] Frontend built and deployed
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Monitoring setup
- [ ] All features tested

**Your Nilam Bangladesh marketplace is now ready for production! 🇧🇩**

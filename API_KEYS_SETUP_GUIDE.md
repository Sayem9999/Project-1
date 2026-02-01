# Nilam Bangladesh - API Keys & Integration Setup Guide

## 🔑 Required API Keys and Credentials

This guide will help you obtain all necessary API keys and credentials for production deployment.

---

## 1. bKash Payment Gateway (Bangladesh)

### What it's for:
Primary payment method for Bangladesh customers

### How to get credentials:

1. **Visit bKash Merchant Portal:**
   - URL: https://developer.bka.sh/
   - Or contact: merchant.marketing@bka.sh

2. **Apply for Merchant Account:**
   - Submit business registration documents
   - Trade license
   - Bank account details
   - NID/Passport of business owner

3. **Complete KYC Process:**
   - Usually takes 5-7 business days
   - bKash team will verify documents

4. **Receive Production Credentials:**
   After approval, you'll receive:
   - **Username**: Your merchant username
   - **Password**: Your merchant password
   - **App Key**: Production app key
   - **App Secret**: Production app secret
   - **Base URL**: `https://tokenized.pay.bka.sh/v1.2.0-beta`

5. **Test Environment (Already Configured):**
   - Username: `sandboxTokenizedUser02`
   - Password: `sandboxTokenizedUser02@12345`
   - App Key: `4f6o0cjiki2rfm34kfdadl1eqq`
   - Test Phone: `01619777283`
   - Test OTP: `123456`
   - Test PIN: `12121`

**Update in:** `/app/backend/.env.production` lines 13-17

**Cost:** 
- Setup Fee: Free
- Transaction Fee: 1.5% (negotiable based on volume)

---

## 2. Google OAuth (Sign in with Google)

### What it's for:
Allow users to sign in with their Google account

### How to get credentials:

1. **Go to Google Cloud Console:**
   - URL: https://console.cloud.google.com/

2. **Create New Project:**
   - Click "New Project"
   - Name: "Nilam Bangladesh"
   - Click "Create"

3. **Enable Google+ API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Consent Screen:**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External"
   - Fill in:
     - App name: Nilam Bangladesh
     - User support email: your@email.com
     - Developer contact: your@email.com
   - Add authorized domain: `nilambd.com`
   - Save

5. **Create OAuth Client ID:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "Nilam Bangladesh Web"
   - Authorized JavaScript origins:
     ```
     https://nilambd.com
     https://www.nilambd.com
     ```
   - Authorized redirect URIs:
     ```
     https://nilambd.com/auth/google/callback
     https://api.nilambd.com/api/auth/google/callback
     ```
   - Click "Create"

6. **Copy Credentials:**
   - Client ID: Looks like `123456789-abcdefg.apps.googleusercontent.com`
   - Client Secret: Looks like `GOCSPX-abcdefg123456`

**Update in:**
- Backend: `/app/backend/.env.production` lines 19-21
- Frontend: `/app/frontend/.env.production` line 8

**Cost:** Free (50,000 requests/day)

---

## 3. Firebase (Phone Number Authentication)

### What it's for:
Free SMS verification for phone number login

### How to get credentials:

1. **Go to Firebase Console:**
   - URL: https://console.firebase.google.com/

2. **Create New Project:**
   - Click "Add project"
   - Name: "Nilam Bangladesh"
   - Accept terms
   - Click "Continue"
   - Disable Google Analytics (optional)
   - Click "Create project"

3. **Add Web App:**
   - Click on Web icon (</>) on project homepage
   - App nickname: "Nilam Web"
   - Check "Also set up Firebase Hosting"
   - Click "Register app"

4. **Enable Phone Authentication:**
   - Go to "Build" → "Authentication"
   - Click "Get started"
   - Go to "Sign-in method" tab
   - Click on "Phone"
   - Toggle "Enable"
   - Save

5. **Configure Authorized Domains:**
   - In Authentication → Settings → Authorized domains
   - Add: `nilambd.com` and `www.nilambd.com`

6. **Get Configuration:**
   - Go to Project Settings (gear icon)
   - Scroll down to "Your apps"
   - Copy Firebase configuration object:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "nilam-bangladesh.firebaseapp.com",
  projectId: "nilam-bangladesh",
  storageBucket: "nilam-bangladesh.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};
```

**Update in:** `/app/frontend/.env.production` lines 11-17

**Free Tier Limits:**
- Phone Auth: 10,000 verifications/month FREE
- SMS costs: $0.01-0.06 per SMS (varies by country)
- For Bangladesh: ~$0.02 per SMS

**Cost:** Free for first 10K/month, then pay-as-you-go

---

## 4. MongoDB Atlas (Production Database)

### What it's for:
Cloud-hosted MongoDB database (more reliable than local)

### How to get credentials:

1. **Sign up for MongoDB Atlas:**
   - URL: https://www.mongodb.com/cloud/atlas/register

2. **Create Free Cluster:**
   - Choose "Shared" (Free M0 tier)
   - Cloud Provider: AWS
   - Region: Singapore (closest to Bangladesh)
   - Cluster Name: "nilam-prod"
   - Click "Create"

3. **Configure Security:**
   - **Network Access:**
     - Click "Network Access" in sidebar
     - Click "Add IP Address"
     - Click "Allow Access from Anywhere" (or add your server IP)
     - Confirm

   - **Database Access:**
     - Click "Database Access" in sidebar
     - Click "Add New Database User"
     - Username: `nilam_admin`
     - Password: Generate secure password
     - Database User Privileges: "Atlas admin"
     - Add User

4. **Get Connection String:**
   - Go to "Database" in sidebar
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Driver: Python 3.12 or later
   - Copy connection string:
     ```
     mongodb+srv://nilam_admin:<password>@nilam-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - Replace `<password>` with your database password

**Update in:** `/app/backend/.env.production` line 2

**Free Tier:**
- Storage: 512 MB
- RAM: Shared
- Perfect for starting out!

**Cost:** Free tier available, paid plans start at $9/month

---

## 5. Supabase (Real-Time Database)

### What it's for:
Real-time bid synchronization across users

### Already Configured! ✅

Your credentials are already in the app:
- URL: `https://yfaooabmdubvpqaxhhwa.supabase.co`
- Anon Key: Already configured

### Just need to create tables:

1. **Go to Supabase Dashboard:**
   - URL: https://supabase.com/dashboard
   - Login to your account

2. **Select Your Project**

3. **Open SQL Editor:**
   - Click "SQL Editor" in left sidebar
   - Click "New query"

4. **Run This SQL Script:**

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

-- Enable Row Level Security
ALTER TABLE public.bids ENABLE ROW LEVEL SECURITY;

-- Allow read access to all users
CREATE POLICY "Allow read access to all users" ON public.bids
  FOR SELECT
  USING (true);

-- Enable real-time (IMPORTANT!)
ALTER PUBLICATION supabase_realtime ADD TABLE public.bids;

-- Verify real-time is enabled
SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
```

5. **Click "Run"**

6. **Verify:** You should see the `bids` table in "Table Editor"

**Cost:** Free tier with 500 MB database

---

## 6. Stripe Connect (Optional - Backup Payment)

### What it's for:
International payments, backup to bKash

### How to get credentials:

1. **Sign up for Stripe:**
   - URL: https://dashboard.stripe.com/register

2. **Complete Business Profile:**
   - Business type
   - Business details
   - Bank account for payouts

3. **Enable Stripe Connect:**
   - Go to "Connect" in dashboard
   - Click "Get started"
   - Choose "Standard" or "Express"

4. **Get API Keys:**
   - Go to "Developers" → "API keys"
   - Copy:
     - Publishable key: `pk_live_...`
     - Secret key: `sk_live_...`

**Update in:** `/app/backend/.env.production` (optional)

**Cost:** 2.9% + BDT 3 per transaction

---

## 📝 Quick Setup Checklist

Print this and check off as you complete:

- [ ] bKash merchant account created
- [ ] bKash production credentials obtained
- [ ] Google Cloud project created
- [ ] Google OAuth credentials obtained
- [ ] Firebase project created
- [ ] Firebase config obtained
- [ ] Phone auth enabled in Firebase
- [ ] MongoDB Atlas cluster created
- [ ] MongoDB connection string obtained
- [ ] Supabase tables created
- [ ] Real-time enabled in Supabase
- [ ] All credentials added to `.env.production`
- [ ] SSL certificate obtained for nilambd.com
- [ ] DNS configured for nilambd.com

---

## 🆘 Troubleshooting

### bKash Integration Issues
- **Error: Invalid credentials**
  - Verify you're using production credentials, not sandbox
  - Check BKASH_BASE_URL is production URL

### Google OAuth Not Working
- **Error: redirect_uri_mismatch**
  - Add exact callback URL to Google Console
  - Include https:// prefix

### Firebase Phone Auth Fails
- **Error: Invalid app credentials**
  - Verify all Firebase config values
  - Check domain is authorized in Firebase console

### Supabase Real-Time Not Working
- **Bids not updating in real-time**
  - Verify table is added to publication
  - Check Row Level Security policies
  - Test with Supabase realtime inspector

---

## 💰 Total Costs Estimate

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| bKash | Test mode | 1.5% per transaction |
| Google OAuth | 50K requests/day | Free |
| Firebase Phone | 10K SMS/month | $0.02/SMS |
| MongoDB Atlas | 512 MB storage | From $9/month |
| Supabase | 500 MB database | From $25/month |
| Domain (nilambd.com) | N/A | ~$12/year |
| SSL Certificate | Free (Let's Encrypt) | Free |
| Server (DigitalOcean) | N/A | From $5/month |

**Estimated Monthly Cost to Start:** $5-20/month (minimal traffic)

---

## ✅ Ready for Production?

Once you have all API keys:

1. Update both `.env.production` files
2. Follow the DEPLOYMENT_GUIDE.md
3. Deploy to nilambd.com
4. Test all features
5. Launch! 🚀

**Need help?** Review the DEPLOYMENT_GUIDE.md for step-by-step instructions.

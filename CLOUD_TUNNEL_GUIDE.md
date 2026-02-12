# Step-by-Step: Host Your API on Your PC (Free & Secure)

By following this guide, you will expose your local Proedit API to the internet securely.

## 1. Install Cloudflared
Download and install the Cloudflare Tunnel daemon for Windows:
- **Direct Link**: [cloudflared-windows-amd64.msi](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi)
- Run the installer.

## 2. Authenticate
Open PowerShell as Administrator and run:
```powershell
cloudflared tunnel login
```
A browser will open. Select your domain (or a free Cloudflare domain) to authorize.

## 3. Create the Tunnel
Run this command to create a tunnel named `proedit-api`:
```powershell
cloudflared tunnel create proedit-api
```
This will generate a **Tunnel ID** (a long string of letters/numbers). Copy it.

## 4. Configure the Tunnel
Create a file named `config.yml` in `%USERPROFILE%\.cloudflared\` with this content:
```yaml
url: http://localhost:8000
tunnel: <YOUR_TUNNEL_ID>
credentials-file: C:\Users\<YOUR_USER>\.cloudflared\<YOUR_TUNNEL_ID>.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

## 5. Route to Your Subdomain
Run this command to create a DNS record for your subdomain:
```powershell
cloudflared tunnel route dns proedit-api api.yourdomain.com
```

## 6. Run the Tunnel
To start the tunnel, run:
```powershell
cloudflared tunnel run proedit-api
```

## 7. Start the API
In another terminal, run your new production script:
```powershell
.\backend\start_production_local.ps1
```

---

### Final Step: Update Vercel
Go to your Vercel Dashboard and update `NEXT_PUBLIC_API_URL` to `https://api.yourdomain.com`.
 Redeploy your frontend, and you're live from your own PC! 🚀

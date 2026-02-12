# Step-by-Step: Host Your API on Your PC (Free & Secure)

By following this guide, you will expose your local Proedit API to the internet securely.

## 1. Install Cloudflared
Download and install the Cloudflare Tunnel daemon for Windows:
- **Direct Link**: [cloudflared-windows-amd64.msi](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi)
- Run the installer.

## Option A: Using Your Own Domain (Permanent)
1. **Login**: `cloudflared tunnel login`
2. **Create**: `cloudflared tunnel create proedit-api`
3. **Route**: `cloudflared tunnel route dns proedit-api api.yourdomain.com`
4. **Run**: `cloudflared tunnel run proedit-api`

## Option B: No Domain (TryCloudflare - Fast & Free)
If you don't own a domain, you can use Cloudflare's "Quick Tunnel". 
**Note**: The URL will change every time you restart the tunnel.

Run this command:
```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000
```
Look for a line in the terminal that says:
`Your quick tunnel has been created! Visit it at: https://some-random-words.trycloudflare.com`

---

## 7. Update Your Frontend
In another terminal, run your new production script:
```powershell
.\backend\start_production_local.ps1
```

---

### Final Step: Update Vercel
Go to your Vercel Dashboard and update `NEXT_PUBLIC_API_URL` to `https://api.yourdomain.com`.
 Redeploy your frontend, and you're live from your own PC! 🚀

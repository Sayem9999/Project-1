# Your Permanent Free API URL (via Tailscale Funnel)

Tailscale Funnel gives you a **Fixed URL** that never changes, even if you restart your computer.

## 1. Setup Tailscale (One-Time)
1. **Login**: Open the Tailscale app on your PC and log in.
2. **Enable MagicDNS**: 
   - Go to the [Tailscale DNS Settings](https://login.tailscale.com/admin/dns).
   - Ensure **MagicDNS** is "Enabled".
3. **Enable Funnel**:
   - Go to the [Tailscale Settings](https://login.tailscale.com/admin/settings/funnel).
   - Ensure **Funnel** is "Enabled".

## 2. Start the Funnel in Pinokio
1. Open **Pinokio**.
2. Click **Start API Only**.
3. Click **Start Tailscale Funnel (Fixed URL)**.
4. Look at the logs for your new permanent URL (e.g., `https://your-pc.tail-name.ts.net`).

## 3. Update Vercel
Go to your Vercel Dashboard and update `NEXT_PUBLIC_API_BASE` to:
`https://your-pc.tail-name.ts.net/api`

---

**You're all set!** No more changing URLs. Your PC is now a permanent server. 🚀

module.exports = {
  title: "ProEdit API",
  description: "High-performance Local API for Proedit (Modal + Vercel Integrated)",
  icon: "icon.png",
  menu: [
    {
      html: '<i class="fa-solid fa-play"></i> Start Proedit Hub (All)',
      href: "start.json"
    },
    {
      html: '<i class="fa-solid fa-desktop"></i> Start Frontend Only',
      href: "frontend.json"
    },
    {
      html: '<i class="fa-solid fa-server"></i> Start API Only',
      href: "api.json"
    },
    {
      html: '<i class="fa-solid fa-robot"></i> Start Worker Only',
      href: "worker.json"
    },
    {
      html: '<i class="fa-solid fa-shield-halved"></i> Start Tailscale Funnel (Fixed URL)',
      href: "tailscale.json"
    },
    {
      html: '<i class="fa-solid fa-terminal"></i> Local Hosting Guide',
      href: "LOCAL_HOSTING_GUIDE.md"
    },
    {
      html: '<i class="fa-solid fa-rotate"></i> Update Hub',
      href: "update.json"
    },
    {
      html: '<i class="fa-solid fa-gear"></i> View Settings',
      href: "backend/.env"
    }
  ]
}

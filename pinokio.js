module.exports = {
  title: "ProEdit API",
  description: "High-performance Local API for Proedit (Modal + Vercel Integrated)",
  icon: "icon.png",
  menu: [
    {
      html: '<i class="fa-solid fa-play"></i> Start Proedit Hub',
      href: "start.json"
    },
    {
      html: '<i class="fa-solid fa-rotate"></i> Restart Hub',
      href: "start.json"
    },
    {
      html: '<i class="fa-solid fa-plug"></i> Install Dependencies',
      href: "install.json"
    },
    {
      html: '<i class="fa-solid fa-terminal"></i> Tunnel Guide',
      href: "CLOUD_TUNNEL_GUIDE.md"
    },
    {
      html: '<i class="fa-solid fa-gear"></i> View Settings',
      href: "backend/.env"
    }
  ]
}

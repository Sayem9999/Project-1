module.exports = {
  title: "ProEdit API",
  description: "High-performance Local API for Proedit (Modal + Vercel Integrated)",
  icon: "icon.png",
  menu: [
    {
      html: '<i class="fa-solid fa-play text-green-400"></i> <b>Start Proedit Hub (Full Stack)</b>',
      href: "start.json"
    },
    {
      html: '<i class="fa-solid fa-robot text-cyan-400"></i> Check AI Readiness (Ollama)',
      href: "ollama.json"
    },
    {
      html: '<hr>'
    },
    {
      html: '<i class="fa-solid fa-code-branch text-orange-500"></i> Start n8n Automation',
      href: "n8n.json"
    },
    {
      html: '<i class="fa-solid fa-desktop"></i> Start Frontend (Dev Mode)',
      href: "frontend.json"
    },
    {
      html: '<i class="fa-solid fa-server"></i> Start API Server',
      href: "api.json"
    },
    {
      html: '<i class="fa-solid fa-microchip"></i> Start Background Worker',
      href: "worker.json"
    },
    {
      html: '<i class="fa-solid fa-shield-halved"></i> Enable Remote Access (Tailscale)',
      href: "tailscale.json"
    },
    {
      html: '<hr>'
    },
    {
      html: '<i class="fa-solid fa-rotate text-blue-400"></i> Update & Reinstall Dependencies',
      href: "update.json"
    },
    {
      html: '<i class="fa-solid fa-vial text-purple-400"></i> <b>Professional E2E Check</b>',
      href: "pro_e2e.json"
    },
    {
      html: '<i class="fa-solid fa-database text-yellow-500"></i> Database Audit (Live)',
      href: "inspect_db.json"
    },
    {
      html: '<i class="fa-solid fa-gear"></i> System Diagnostics',
      href: "backend/.env"
    }
  ]
}

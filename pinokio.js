module.exports = {
  title: "ProEdit API (Updated)",
  description: "High-performance Local API for Proedit (Modal + Vercel Integrated)",
  icon: "icon.png",
  menu: [
    {
      html: '<i class="fa-solid fa-code-branch text-orange-500"></i> <b>Start n8n Automation</b>',
      href: "n8n.json"
    },
    {
      html: '<hr>'
    },
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
      html: '<hr>'
    },
    {
      html: '<b>PRO STUDIO INTELLIGENCE</b>'
    },
    {
      html: '<i class="fa-solid fa-microphone-lines text-pink-400"></i> Cinematic Audio Audit (Phase 7)',
      href: "test_audio.json"
    },
    {
      html: '<i class="fa-solid fa-wand-magic-sparkles text-yellow-400"></i> Social Graphics Audit (Phase 8)',
      href: "test_graphics.json"
    },
    {
      html: '<i class="fa-solid fa-magnifying-glass text-cyan-400"></i> Semantic Scout Audit (Phase 6)',
      href: "test_scout.json"
    },
    {
      html: '<i class="fa-solid fa-vial text-purple-400"></i> <b>Full Hollywood E2E Check</b>',
      href: "pro_e2e.json"
    },
    {
      html: '<hr>'
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

import { NextRequest } from "next/server";

// Server-side proxy to avoid browser CORS + Private Network Access (PNA) issues
// when calling a Tailscale Funnel endpoint from a Vercel-hosted frontend.
//
// Configure on Vercel:
// - NEXT_PUBLIC_API_BASE=/api/proxy
// - API_UPSTREAM_BASE=https://<your-tailnet-host>.ts.net/api
//
// For local dev, you can skip these and use NEXT_PUBLIC_API_BASE=http://localhost:8000/api

const UPSTREAM = process.env.API_UPSTREAM_BASE;

function joinUrl(base: string, path: string): string {
  const b = base.replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${b}${p}`;
}

async function handle(req: NextRequest, ctx: { params: Promise<{ path?: string[] }> }) {
  if (!UPSTREAM) {
    return new Response(
      JSON.stringify({
        detail:
          "API_UPSTREAM_BASE is not set on the server. Set it to e.g. https://desktop-ajdgsgd.tail4e4049.ts.net/api",
      }),
      { status: 500, headers: { "content-type": "application/json" } }
    );
  }

  const { path = [] } = await ctx.params;
  const upstreamPath = `/${path.join("/")}`;

  const upstreamUrl = new URL(joinUrl(UPSTREAM, upstreamPath));

  // Preserve querystring
  req.nextUrl.searchParams.forEach((value, key) => {
    upstreamUrl.searchParams.append(key, value);
  });

  // Forward headers, but strip hop-by-hop and problematic ones.
  const headers = new Headers(req.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");

  const method = req.method.toUpperCase();
  const hasBody = !(method === "GET" || method === "HEAD");
  const body = hasBody ? await req.arrayBuffer() : undefined;

  const upstreamRes = await fetch(upstreamUrl.toString(), {
    method,
    headers,
    body,
    redirect: "manual",
  });

  // Stream response back
  const resHeaders = new Headers(upstreamRes.headers);
  resHeaders.delete("content-encoding"); // let Vercel handle encoding
  resHeaders.delete("content-length");

  return new Response(upstreamRes.body, {
    status: upstreamRes.status,
    headers: resHeaders,
  });
}

export async function GET(req: NextRequest, ctx: any) {
  return handle(req, ctx);
}
export async function POST(req: NextRequest, ctx: any) {
  return handle(req, ctx);
}
export async function PUT(req: NextRequest, ctx: any) {
  return handle(req, ctx);
}
export async function PATCH(req: NextRequest, ctx: any) {
  return handle(req, ctx);
}
export async function DELETE(req: NextRequest, ctx: any) {
  return handle(req, ctx);
}
export async function OPTIONS(req: NextRequest, ctx: any) {
  return handle(req, ctx);
}


export const API_BASE =
  (process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api").replace(/\/$/, "");

export const API_ORIGIN = API_BASE.endsWith("/api")
  ? API_BASE.slice(0, -4)
  : API_BASE;

export class ApiError extends Error {
  status: number;
  code?: string;
  isAuth: boolean;
  raw?: any;

  constructor(message: string, status: number, code?: string, isAuth = false, raw?: any) {
    super(message);
    this.status = status;
    this.code = code;
    this.isAuth = isAuth;
    this.raw = raw;
  }
}

type ApiOptions = Omit<RequestInit, "body"> & {
  auth?: boolean;
  body?: any;
};

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("token", token);
}

export function setStoredUser(user: unknown): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("user", JSON.stringify(user));
}

export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

function buildUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  if (!path.startsWith("/")) {
    return `${API_BASE}/${path}`;
  }
  return `${API_BASE}${path}`;
}

async function safeJson(res: Response): Promise<any | null> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

function normalizeMessage(data: any): { message: string; code?: string } {
  const detail = data?.detail ?? data?.message ?? data;
  if (Array.isArray(detail)) {
    const joined = detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .join("; ");
    return { message: joined || "Request failed", code: data?.error_code };
  }
  if (typeof detail === "string") {
    return { message: detail, code: data?.error_code };
  }
  if (detail?.message) {
    return { message: detail.message, code: detail.error_code ?? data?.error_code };
  }
  if (detail && typeof detail === "object") {
    return { message: JSON.stringify(detail), code: data?.error_code };
  }
  return { message: "Request failed", code: data?.error_code };
}

async function toApiError(res: Response): Promise<ApiError> {
  const data = await safeJson(res);
  const { message, code } = normalizeMessage(data);
  const lowered = message.toLowerCase();
  const isAuth =
    res.status === 401 ||
    (res.status === 403 &&
      (code === "auth_failed" ||
        lowered.includes("not authenticated") ||
        lowered.includes("invalid token") ||
        lowered.includes("authorization")));
  return new ApiError(message, res.status, code, isAuth, data);
}

function withHeaders(options: ApiOptions): RequestInit {
  const headers = new Headers(options.headers || {});
  const body = options.body;

  if (options.auth) {
    const token = getAuthToken();
    if (!token) {
      throw new ApiError("Authentication required", 401, "auth_failed", true);
    }
    headers.set("Authorization", `Bearer ${token}`);
  }

  const isFormData =
    typeof FormData !== "undefined" && body instanceof FormData;
  const isBlob = typeof Blob !== "undefined" && body instanceof Blob;
  const isString = typeof body === "string";

  if (body && !isFormData && !isBlob && !isString) {
    headers.set("Content-Type", "application/json");
    return { ...options, headers, body: JSON.stringify(body) };
  }

  return { ...options, headers };
}

export async function apiFetch(path: string, options: ApiOptions = {}): Promise<Response> {
  const res = await fetch(buildUrl(path), withHeaders(options));
  if (!res.ok) {
    throw await toApiError(res);
  }
  return res;
}

export async function apiRequest<T = any>(path: string, options: ApiOptions = {}): Promise<T> {
  const res = await apiFetch(path, options);
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return (await res.json()) as T;
  }
  return (await res.text()) as T;
}

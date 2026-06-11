/**
 * Typed wrapper around the backend REST API.
 *
 * `API_BASE` defaults to `http://localhost:8000` for local dev. Override
 * by setting `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` or at
 * the hosting provider for production.
 */

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// ─────────────────────────────────────────────────────────────
// Error shape (shared)
// ─────────────────────────────────────────────────────────────

export interface FieldError {
  field: string;
  message: string;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public fieldErrors: FieldError[],
    message: string,
  ) {
    super(message);
  }
}

interface PydanticErrorDetail {
  type: string;
  loc: (string | number)[];
  msg: string;
}

interface ErrorBody {
  detail?: PydanticErrorDetail[] | string;
}

/**
 * Internal: POST JSON, expect a 2xx, parse errors into ApiError. Used
 * by every public endpoint helper below.
 *
 * `credentials: "include"` is required so the browser:
 *   1. Accepts Set-Cookie from cross-origin responses (e.g. /auth/login
 *      setting access_token + refresh_token on :8000 → :3000).
 *   2. Sends those cookies back on subsequent requests.
 * The backend's CORS middleware already has allow_credentials=True.
 */
async function postJson<T>(path: string, body: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "include",
    });
  } catch {
    throw new ApiError(
      0,
      [],
      "Could not reach the server. Please check your connection.",
    );
  }

  if (res.status >= 200 && res.status < 300) {
    return (await res.json()) as T;
  }

  const errBody = (await res.json().catch(() => ({}))) as ErrorBody;
  const fieldErrors: FieldError[] = [];

  if (Array.isArray(errBody.detail)) {
    for (const item of errBody.detail) {
      const path = item.loc.filter((p) => p !== "body").map(String);
      fieldErrors.push({
        field: path[path.length - 1] ?? "",
        message: item.msg,
      });
    }
  }

  let topMessage = "Something went wrong. Please try again.";
  if (res.status === 422) {
    topMessage = "Please fix the highlighted fields and resubmit.";
  } else if (res.status === 429) {
    topMessage =
      "Too many submissions — please wait a minute and try again.";
  } else if (res.status === 409 && typeof errBody.detail === "string") {
    topMessage = errBody.detail;
  } else if (typeof errBody.detail === "string") {
    topMessage = errBody.detail;
  }

  throw new ApiError(res.status, fieldErrors, topMessage);
}

// ─────────────────────────────────────────────────────────────
// Applications (POST /applications) — S6
// ─────────────────────────────────────────────────────────────

export type ClassLevel =
  | "nursery"
  | "primary"
  | "junior_secondary"
  | "senior_secondary";

export type ApplicationStatus =
  | "new"
  | "contacted"
  | "enrolled"
  | "rejected";

export interface ApplicationCreate {
  child_name: string;
  guardian_name: string;
  email: string;
  phone: string;
  class_level: ClassLevel;
  message?: string;
}

export interface ApplicationResponse {
  id: string;
  status: ApplicationStatus;
  created_at: string;
}

export function postApplication(
  payload: ApplicationCreate,
): Promise<ApplicationResponse> {
  return postJson<ApplicationResponse>("/applications", payload);
}

// ─────────────────────────────────────────────────────────────
// Auth — register (POST /auth/register) — S7
// ─────────────────────────────────────────────────────────────

export type UserRole = "admin" | "instructor" | "student";
export type UserStatus = "pending" | "active" | "suspended";

export interface RegisterRequest {
  name: string;
  email: string;
  phone?: string;
  password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  phone: string | null;
  role: UserRole;
  status: UserStatus;
  created_at: string;
}

export function postRegister(
  payload: RegisterRequest,
): Promise<UserResponse> {
  return postJson<UserResponse>("/auth/register", payload);
}

// ─────────────────────────────────────────────────────────────
// Auth — login / refresh / logout (POST /auth/*) — S8
// ─────────────────────────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
}

export function postLogin(payload: LoginRequest): Promise<UserResponse> {
  return postJson<UserResponse>("/auth/login", payload);
}

export function postRefresh(): Promise<UserResponse> {
  return postJson<UserResponse>("/auth/refresh", {});
}

export function postLogout(): Promise<{ ok: boolean }> {
  return postJson<{ ok: boolean }>("/auth/logout", {});
}

// ─────────────────────────────────────────────────────────────
// Auth — password reset (POST /auth/forgot|reset-password) — S9
// ─────────────────────────────────────────────────────────────

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface GenericOk {
  ok: boolean;
  detail?: string;
}

export function postForgotPassword(
  payload: ForgotPasswordRequest,
): Promise<GenericOk> {
  return postJson<GenericOk>("/auth/forgot-password", payload);
}

export function postResetPassword(
  payload: ResetPasswordRequest,
): Promise<GenericOk> {
  return postJson<GenericOk>("/auth/reset-password", payload);
}

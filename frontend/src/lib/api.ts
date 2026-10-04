/**
 * Typed wrapper around the backend REST API.
 *
 * Calls go to `/api/*` on this same site; `next.config.mjs` proxies them
 * to the backend (`BACKEND_URL`). Same-origin keeps the httpOnly auth
 * cookies first-party, so login works whatever domains the two services
 * end up on.
 */

export const API_BASE = "/api";

const NETWORK_ERROR = "Could not reach the server. Please check your connection.";

/**
 * Fetch with cookies; on a 401 refresh the session once and retry.
 * Access tokens live 15 minutes, so without this a learner mid-lesson
 * would be bounced to sign-in.
 */
async function send(path: string, init: RequestInit): Promise<Response> {
  const go = () => fetch(`${API_BASE}${path}`, { ...init, credentials: "include" });
  let res: Response;
  try {
    res = await go();
    if (res.status === 401 && !path.startsWith("/auth/")) {
      const refreshed = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        credentials: "include",
      });
      if (refreshed.ok) res = await go();
    }
  } catch {
    throw new ApiError(0, [], NETWORK_ERROR);
  }
  return res;
}

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
 * Internal: GET JSON, expect a 2xx, parse errors into ApiError. Used
 * by every authenticated read endpoint helper below.
 */
async function getJson<T>(path: string): Promise<T> {
  const res = await send(path, { method: "GET" });

  if (res.status >= 200 && res.status < 300) {
    return (await res.json()) as T;
  }

  const errBody = (await res.json().catch(() => ({}))) as ErrorBody;
  let topMessage = "Something went wrong. Please try again.";
  if (res.status === 401) topMessage = "Please sign in to continue.";
  else if (res.status === 403) topMessage = "You don't have access to this.";
  else if (res.status === 404) topMessage = "Not found.";
  else if (typeof errBody.detail === "string") topMessage = errBody.detail;

  throw new ApiError(res.status, [], topMessage);
}

/**
 * Internal: POST JSON, expect a 2xx, parse errors into ApiError. Used
 * by every endpoint helper below that sends a body.
 */
async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await send(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

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

// ─────────────────────────────────────────────────────────────
// Payments (POST /payments/*) — S11
// ─────────────────────────────────────────────────────────────

export type PaymentPurpose = "fees" | "programme";
export type PaymentStatus = "pending" | "success" | "failed";

export interface PaymentInitializeRequest {
  purpose: PaymentPurpose;
  target?: string;
}

export interface PaymentInitializeResponse {
  reference: string;
  amount_kobo: number;
  public_key: string;
  payer_email: string;
  purpose: PaymentPurpose;
  target: string | null;
}

export interface PaymentVerifyRequest {
  reference: string;
}

export interface PaymentResponse {
  id: string;
  reference: string;
  amount_kobo: number;
  purpose: PaymentPurpose;
  target: string | null;
  status: PaymentStatus;
  verified_at: string | null;
  created_at: string;
}

export function postPaymentsInitialize(
  payload: PaymentInitializeRequest,
): Promise<PaymentInitializeResponse> {
  return postJson<PaymentInitializeResponse>(
    "/payments/initialize",
    payload,
  );
}

export function postPaymentsVerify(
  payload: PaymentVerifyRequest,
): Promise<PaymentResponse> {
  return postJson<PaymentResponse>("/payments/verify", payload);
}

// ─────────────────────────────────────────────────────────────
// Courses (GET /me/courses, /courses/{id}) — S15
// ─────────────────────────────────────────────────────────────

export type CourseType = "school" | "online";

export interface CourseListItem {
  id: string;
  slug: string;
  title: string;
  type: CourseType;
  level: string;
  summary: string;
  is_paid: boolean;
  progress_percent: number;
}

export interface LessonRead {
  id: string;
  sort_order: number;
  title: string;
  duration_min: number;
  completed: boolean;
}

export interface ModuleRead {
  id: string;
  sort_order: number;
  title: string;
  lessons: LessonRead[];
}

export interface CourseDetail {
  id: string;
  slug: string;
  title: string;
  type: CourseType;
  level: string;
  summary: string;
  is_paid: boolean;
  progress_percent: number;
  modules: ModuleRead[];
}

export function getMeCourses(): Promise<CourseListItem[]> {
  return getJson<CourseListItem[]>("/me/courses");
}

export function getCourse(courseId: string): Promise<CourseDetail> {
  return getJson<CourseDetail>(`/courses/${courseId}`);
}

// ─────────────────────────────────────────────────────────────
// Lesson view (GET /courses/{course_id}/lessons/{lesson_id}) — S16
// ─────────────────────────────────────────────────────────────

export interface LessonNeighbor {
  id: string;
  title: string;
}

export interface LessonDetail {
  id: string;
  sort_order: number;
  title: string;
  content: string;
  duration_min: number;
  media_url: string | null;
  completed: boolean;

  course_id: string;
  course_title: string;
  module_id: string;
  module_title: string;

  prev: LessonNeighbor | null;
  next: LessonNeighbor | null;
}

export function getLesson(
  courseId: string,
  lessonId: string,
): Promise<LessonDetail> {
  return getJson<LessonDetail>(
    `/courses/${courseId}/lessons/${lessonId}`,
  );
}

// ─────────────────────────────────────────────────────────────
// Mark lesson complete (POST /lessons/{id}/complete) — S17
// ─────────────────────────────────────────────────────────────

export interface LessonCompleteResponse {
  lesson_id: string;
  completed: boolean;
  completed_at: string;
  course_id: string;
  progress_percent: number;
}

export function postLessonComplete(
  lessonId: string,
): Promise<LessonCompleteResponse> {
  return postJson<LessonCompleteResponse>(
    `/lessons/${lessonId}/complete`,
    {},
  );
}

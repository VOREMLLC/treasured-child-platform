/**
 * Typed wrapper around the backend REST API.
 *
 * `API_BASE` defaults to `http://localhost:8000` for local dev. Override
 * by setting `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` or at
 * the hosting provider for production.
 */

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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

/** Pydantic validation error item shape, normalised. */
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

export async function postApplication(
  payload: ApplicationCreate,
): Promise<ApplicationResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError(
      0,
      [],
      "Could not reach the server. Please check your connection.",
    );
  }

  if (res.status === 201) {
    return (await res.json()) as ApplicationResponse;
  }

  const body = (await res.json().catch(() => ({}))) as ErrorBody;
  const fieldErrors: FieldError[] = [];

  if (Array.isArray(body.detail)) {
    for (const item of body.detail) {
      // Drop the leading "body" segment from FastAPI loc.
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
  } else if (typeof body.detail === "string") {
    topMessage = body.detail;
  }

  throw new ApiError(res.status, fieldErrors, topMessage);
}

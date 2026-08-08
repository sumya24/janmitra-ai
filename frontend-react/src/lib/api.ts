const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; token?: string | null; formData?: FormData } = {}
): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.token) headers["Authorization"] = `Bearer ${options.token}`;

  let body: BodyInit | undefined;
  if (options.formData) {
    body = options.formData;
  } else if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(options.body);
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { method: options.method || "GET", headers, body });
  } catch {
    throw new ApiError(0, "Could not reach the server. Check your connection and try again.");
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status}).`;
    try {
      const data = await response.json();
      if (data?.detail) detail = data.detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export interface UserProfile {
  id: number;
  full_name: string;
  phone: string;
  role: "citizen" | "worker" | "admin";
  preferred_language: string;
  ward: string | null;
}

export interface AuthResponse {
  access_token: string;
  user: UserProfile;
}

export type ComplaintStatus = "pending" | "assigned" | "accepted" | "resolved";

export interface Complaint {
  id: number;
  citizen_id: string;
  original_text: string;
  original_language: string;
  translated_text: string;
  display_text: string;
  summary: string;
  display_summary: string;
  photo_path: string | null;
  status: ComplaintStatus;
  ward: string | null;
  assigned_worker_name: string | null;
  // Only populated once the assigned worker has accepted (or resolved) — see backend/routes/complaints.py.
  assigned_worker_phone: string | null;
  rejection_count: number;
  feedback_rating: number | null;
  feedback_comment: string | null;
  created_at: string;
}

export interface WorkerSummary extends UserProfile {
  open_complaints: number;
  resolved_complaints: number;
}

export const api = {
  signup: (body: { full_name: string; phone: string; password: string; preferred_language: string }) =>
    request<AuthResponse>("/auth/signup", { method: "POST", body }),

  login: (body: { phone: string; password: string }) =>
    request<AuthResponse>("/auth/login", { method: "POST", body }),

  me: (token: string) => request<UserProfile>("/auth/me", { token }),

  updateMe: (token: string, body: { full_name?: string; preferred_language?: string }) =>
    request<UserProfile>("/auth/me", { method: "PATCH", token, body }),

  listComplaints: (token: string, lang?: string) =>
    request<Complaint[]>(`/complaints${lang ? `?lang=${lang}` : ""}`, { token }),

  listWards: (token: string) => request<string[]>("/complaints/wards", { token }),

  createComplaint: (token: string, form: FormData) =>
    request<Complaint>("/complaints", { method: "POST", token, formData: form }),

  acceptComplaint: (token: string, id: number) =>
    request<Complaint>(`/complaints/${id}/accept`, { method: "POST", token }),

  rejectComplaint: (token: string, id: number) =>
    request<Complaint>(`/complaints/${id}/reject`, { method: "POST", token }),

  resolveComplaint: (token: string, id: number) =>
    request<Complaint>(`/complaints/${id}/resolve`, { method: "POST", token }),

  submitFeedback: (token: string, id: number, body: { rating: number; comment?: string }) =>
    request<Complaint>(`/complaints/${id}/feedback`, { method: "POST", token, body }),

  createWorker: (
    token: string,
    body: { full_name: string; phone: string; password: string; ward: string; preferred_language: string }
  ) => request<UserProfile>("/admin/workers", { method: "POST", token, body }),

  listWorkers: (token: string) => request<WorkerSummary[]>("/admin/workers", { token }),

  photoUrl: (filename: string) => `${API_URL}/uploads/${filename}`,
};

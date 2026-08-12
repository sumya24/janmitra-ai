import type { AskJanMitraConversationTurn, AskJanMitraResponse, AskVoiceResponse } from "./ragTypes";

// Falls back to "" (same-origin, relative requests) when unset -- the production Docker build
// deliberately leaves VITE_API_URL unset so requests go through Caddy's same-origin reverse
// proxy (see deploy/Caddyfile) with no CORS hop. Local dev sets VITE_API_URL explicitly via
// .env (copied from .env.example) to reach the backend dev server on a different port.
const API_URL = import.meta.env.VITE_API_URL || "";

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

/** Fetch a binary (PDF) response, rather than JSON -- used only by downloadComplaintReport().
 * Auth still goes through the same Bearer header as everything else (no separate, weaker
 * authorization path for the download endpoint -- see backend/routes/complaints.py). Filename
 * comes from the server's Content-Disposition header, the same real value the backend derived
 * from the complaint's own display id -- never guessed or reconstructed client-side. */
async function requestBlob(path: string, token: string): Promise<{ blob: Blob; filename: string }> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { headers: { Authorization: `Bearer ${token}` } });
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
  const disposition = response.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename="?([^";]+)"?/);
  const filename = match ? match[1] : "report.pdf";
  return { blob: await response.blob(), filename };
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

export type ComplaintStatus = "pending" | "assigned" | "accepted" | "in_progress" | "resolved";

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
  address: string | null;
  // Human-readable names for whatever structured location could be resolved -- None at any
  // level that wasn't resolved (see backend's LocationResolver). Never a fabricated value.
  location_state: string | null;
  location_district: string | null;
  location_ulb: string | null;
  assigned_worker_name: string | null;
  // Only populated once the assigned worker has accepted (or resolved) — see backend/routes/complaints.py.
  assigned_worker_phone: string | null;
  rejection_count: number;
  feedback_rating: number | null;
  feedback_comment: string | null;
  created_at: string;
}

// GET /complaints/area-summary -- deliberately a small, separate shape rather than reusing
// Complaint: no citizen_id, no assigned_worker_name/phone anywhere here, since this is a
// neighbor's complaint, not the caller's own (see backend's AreaSummaryResponse docstring).
export interface AreaComplaintSummary {
  id: number;
  status: ComplaintStatus;
  display_text: string;
  created_at: string;
  status_updated_at: string;
}

export interface AreaSummary {
  ward: string;
  pending_count: number;
  in_progress_count: number;
  resolved_count: number;
  complaints: AreaComplaintSummary[];
}

// Worker complaint-resolution workflow -- see backend/routes/complaints.py's
// ComplaintUpdateResponse / StatusHistoryEntryResponse / ComplaintDetailResponse.
export type ComplaintUpdateType = "INITIAL_ASSESSMENT" | "PROGRESS_UPDATE" | "COMPLETION";

// Evidence upload phase -- see backend/models.py's ComplaintEvidence docstring. One row per
// uploaded file; a complaint/update can have zero to many, unlike the old single `photo_path`
// columns (kept alongside these, read-only, for rows written before this system existed).
export type EvidenceStage = "CITIZEN_COMPLAINT" | "INITIAL_ASSESSMENT" | "PROGRESS_UPDATE" | "COMPLETION";

export interface EvidenceFile {
  id: number;
  update_id: number | null;
  uploaded_by: number;
  uploader_role: "citizen" | "worker";
  file_name: string;
  file_path: string;
  file_type: string;
  file_size: number;
  stage: EvidenceStage;
  created_at: string;
}

export interface ComplaintUpdateEntry {
  id: number;
  update_type: ComplaintUpdateType;
  text: string;
  photo_path: string | null;
  worker_name: string | null;
  created_at: string;
  evidence: EvidenceFile[];
}

export interface StatusHistoryEntry {
  from_status: string | null;
  to_status: string;
  actor_role: "citizen" | "worker" | "system" | "admin";
  note: string | null;
  created_at: string;
}

export interface ComplaintDetail extends Complaint {
  updates: ComplaintUpdateEntry[];
  status_history: StatusHistoryEntry[];
  // Every evidence file across every stage -- group by `.stage` (and, within PROGRESS_UPDATE,
  // by `.update_id`) to show citizen/initial/progress/completion evidence separately.
  evidence: EvidenceFile[];
}

export interface ComplaintReport {
  complaint_id: number;
  display_id: string;
  service_summary: string;
  original_description: string;
  created_at: string;
  location_ward: string | null;
  location_state: string | null;
  location_district: string | null;
  location_ulb: string | null;
  location_address: string | null;
  assigned_worker_name: string | null;
  initial_assessment: string | null;
  initial_assessment_at: string | null;
  progress_updates: { text: string; photo_path: string | null; worker_name: string | null; created_at: string; evidence: string[] }[];
  completion_status: string | null;
  completion_evidence_photo: string | null;
  resolved_at: string | null;
  timeline: { from_status: string | null; to_status: string; actor_role: string; note: string | null; created_at: string }[];
  citizen_evidence: string[];
  initial_assessment_evidence: string[];
  completion_evidence: string[];
}

// In-app notifications -- see backend/routes/notifications.py. NEW_ASSIGNMENT/REASSIGNED go to
// workers (created by assignment_service.py). AI_ALERT goes to every admin, created by
// backend/repositories/ai_request_log_repository.py's check_and_fire_alerts() when the Ask
// JanMitra pipeline's rolling error rate or latency crosses a threshold -- see that function's
// docstring for the cooldown that keeps a sustained problem from spamming a notification per
// request. AI_ALERT notifications never have a complaint_id (see NotificationBell.tsx).
export type NotificationType = "NEW_ASSIGNMENT" | "REASSIGNED" | "AI_ALERT";

export interface AppNotification {
  id: number;
  type: NotificationType;
  title: string;
  message: string;
  complaint_id: number | null;
  created_at: string;
  read_at: string | null;
}

export interface NotificationList {
  notifications: AppNotification[];
  unread_count: number;
}

export interface WorkerSummary extends UserProfile {
  open_complaints: number;
  resolved_complaints: number;
}

export interface DeleteWorkerResult {
  deleted_worker_id: number;
  // How many of this worker's "assigned"/"accepted" complaints were reset to "pending" as a
  // result — see backend/routes/admin.py's delete_worker() docstring for why they're reset,
  // never deleted, along with the worker.
  reset_to_pending: number;
}

export interface DeleteComplaintResult {
  deleted_complaint_id: number;
}

export interface AssignComplaintResult {
  id: number;
  status: ComplaintStatus;
  assigned_worker_id: number | null;
  assigned_worker_name: string | null;
}

// AI Monitoring (Admin dashboard) -- see backend/routes/admin.py's /admin/ai-monitoring*
// endpoints and docs/ask_janmitra_langsmith_observability.md. Sourced entirely from the app's
// own database (AiRequestLog), never from LangSmith directly -- this keeps working even when
// LangSmith isn't configured; `trace_url` is the only field that ever comes from LangSmith
// config, and it's just a locally-built string, not a live LangSmith API call.
export interface AiMonitoringSummary {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  error_rate: number;
  average_latency_ms: number;
  rag_requests: number;
  complaint_requests: number;
  status_requests: number;
  out_of_scope_requests: number;
  clarification_requests: number;
}

export interface AiRequestLogEntry {
  id: number;
  request_id: string;
  intent: string | null;
  service_category: string | null;
  routed_to: string;
  success: boolean;
  error_type: string | null;
  latency_ms: number;
  created_at: string;
  trace_url: string | null;
}

export const api = {
  // ward is mandatory, one-time-at-signup -- see SignupRequest.ward's docstring (backend/routes/
  // auth.py). Not present on updateMe below: it's deliberately not editable later.
  signup: (body: { full_name: string; phone: string; password: string; preferred_language: string; ward: string }) =>
    request<AuthResponse>("/auth/signup", { method: "POST", body }),

  login: (body: { phone: string; password: string }) =>
    request<AuthResponse>("/auth/login", { method: "POST", body }),

  me: (token: string) => request<UserProfile>("/auth/me", { token }),

  updateMe: (token: string, body: { full_name?: string; preferred_language?: string }) =>
    request<UserProfile>("/auth/me", { method: "PATCH", token, body }),

  listComplaints: (token: string, lang?: string, workerId?: number) => {
    const params = new URLSearchParams();
    if (lang) params.set("lang", lang);
    if (workerId !== undefined) params.set("worker_id", String(workerId));
    const qs = params.toString();
    return request<Complaint[]>(`/complaints${qs ? `?${qs}` : ""}`, { token });
  },

  // Deliberately no required token -- GET /complaints/wards is unauthenticated (see its own
  // docstring), since Signup needs this list before the citizen has one at all.
  listWards: (token?: string) => request<string[]>("/complaints/wards", token ? { token } : {}),

  getAreaSummary: (token: string, lang?: string) =>
    request<AreaSummary>(`/complaints/area-summary${lang ? `?lang=${lang}` : ""}`, { token }),

  createComplaint: (token: string, form: FormData) =>
    request<Complaint>("/complaints", { method: "POST", token, formData: form }),

  // Full detail view (complaint + status timeline + worker-authored updates) -- the data source
  // for the worker task-detail page and the citizen-facing timeline alike. Same authorization
  // the list endpoint already applies (citizen owns it / worker is currently assigned / admin
  // sees everything), enforced server-side -- see backend/routes/complaints.py's
  // _get_visible_complaint.
  getComplaint: (token: string, id: number, lang?: string) =>
    request<ComplaintDetail>(`/complaints/${id}${lang ? `?lang=${lang}` : ""}`, { token }),

  acceptComplaint: (token: string, id: number) =>
    request<Complaint>(`/complaints/${id}/accept`, { method: "POST", token }),

  // `reason` is mandatory -- see RejectComplaintModal, which blocks submission with an empty
  // reason client-side; the backend independently re-validates this (never trust the frontend
  // alone for a hard rule -- see backend/routes/complaints.py's reject_complaint()).
  rejectComplaint: (token: string, id: number, reason: string) =>
    request<Complaint>(`/complaints/${id}/reject`, { method: "POST", token, body: { reason } }),

  // Mandatory initial assessment -- moves an accepted complaint to "in_progress". `photos` is
  // optional evidence (zero or more) -- see StartWorkModal. Now multipart/form-data (was JSON)
  // so it can carry files, matching /resolve's existing contract.
  startWork: (token: string, id: number, assessment: string, photos?: File[]) => {
    const form = new FormData();
    form.append("assessment", assessment);
    for (const photo of photos ?? []) form.append("photos", photo);
    return request<Complaint>(`/complaints/${id}/start`, { method: "POST", token, formData: form });
  },

  // Optional -- a worker may add zero, one, or many of these while a complaint is in_progress.
  // `photos` is optional evidence (zero or more), reusing the same upload path every other photo
  // in this app already uses.
  addProgressUpdate: (token: string, id: number, text: string, photos?: File[]) => {
    const form = new FormData();
    form.append("text", text);
    for (const photo of photos ?? []) form.append("photos", photo);
    return request<ComplaintUpdateEntry>(`/complaints/${id}/updates`, { method: "POST", token, formData: form });
  },

  // `completion_status` is mandatory (blocks the complaint moving to "resolved" without one --
  // see backend/routes/complaints.py's resolve_complaint() docstring for the commit-ordering
  // guarantee); `photos` is optional completion evidence (zero or more).
  resolveComplaint: (token: string, id: number, completionStatus: string, photos?: File[]) => {
    const form = new FormData();
    form.append("completion_status", completionStatus);
    for (const photo of photos ?? []) form.append("photos", photo);
    return request<Complaint>(`/complaints/${id}/resolve`, { method: "POST", token, formData: form });
  },

  submitFeedback: (token: string, id: number, body: { rating: number; comment?: string }) =>
    request<Complaint>(`/complaints/${id}/feedback`, { method: "POST", token, body }),

  // Resolution report -- both 404 (via the shared ApiError) until the complaint is actually
  // "resolved"; never a fake/partial report before then (see backend/routes/complaints.py).
  getComplaintReport: (token: string, id: number) => request<ComplaintReport>(`/complaints/${id}/report`, { token }),

  downloadComplaintReport: (token: string, id: number) => requestBlob(`/complaints/${id}/report/download`, token),

  // In-app notifications -- worker-only in practice today, see AppNotification's docstring.
  listNotifications: (token: string) => request<NotificationList>("/notifications", { token }),

  markNotificationRead: (token: string, id: number) =>
    request<AppNotification>(`/notifications/${id}/read`, { method: "POST", token }),

  createWorker: (
    token: string,
    body: { full_name: string; phone: string; password: string; ward: string; preferred_language: string }
  ) => request<UserProfile>("/admin/workers", { method: "POST", token, body }),

  listWorkers: (token: string) => request<WorkerSummary[]>("/admin/workers", { token }),

  updateWorker: (token: string, id: number, body: { full_name?: string; ward?: string; preferred_language?: string }) =>
    request<UserProfile>(`/admin/workers/${id}`, { method: "PATCH", token, body }),

  resetWorkerPassword: (token: string, id: number, newPassword: string) =>
    request<UserProfile>(`/admin/workers/${id}/reset-password`, { method: "POST", token, body: { new_password: newPassword } }),

  deleteWorker: (token: string, id: number) =>
    request<DeleteWorkerResult>(`/admin/workers/${id}`, { method: "DELETE", token }),

  deleteComplaint: (token: string, id: number) =>
    request<DeleteComplaintResult>(`/admin/complaints/${id}`, { method: "DELETE", token }),

  assignComplaint: (token: string, complaintId: number, workerId: number) =>
    request<AssignComplaintResult>(`/admin/complaints/${complaintId}/assign`, {
      method: "POST",
      token,
      body: { worker_id: workerId },
    }),

  aiMonitoringSummary: (token: string) => request<AiMonitoringSummary>("/admin/ai-monitoring", { token }),

  aiMonitoringRequests: (token: string, limit = 20) =>
    request<AiRequestLogEntry[]>(`/admin/ai-monitoring/requests?limit=${limit}`, { token }),

  askJanMitra: (
    token: string,
    body: {
      question: string;
      language: string;
      latitude?: number | null;
      longitude?: number | null;
      location_text?: string | null;
      conversation_history?: AskJanMitraConversationTurn[];
    }
  ) => request<AskJanMitraResponse>("/ask-janmitra", { method: "POST", token, body }),

  // Same request as askJanMitra(), plus one attached photo -- multipart because it carries a
  // file (see backend/routes/ask_janmitra.py's POST /ask-janmitra/image). conversation_history
  // is JSON-encoded into its own form field since multipart can't nest structured values, same
  // shape the JSON endpoint already validates.
  askJanMitraWithImage: (
    token: string,
    body: {
      question: string;
      language: string;
      latitude?: number | null;
      longitude?: number | null;
      location_text?: string | null;
      conversation_history?: AskJanMitraConversationTurn[];
      image: File;
    }
  ) => {
    const form = new FormData();
    form.append("question", body.question);
    form.append("language", body.language);
    if (body.latitude != null) form.append("latitude", String(body.latitude));
    if (body.longitude != null) form.append("longitude", String(body.longitude));
    if (body.location_text) form.append("location_text", body.location_text);
    form.append("conversation_history", JSON.stringify(body.conversation_history ?? []));
    form.append("image", body.image);
    return request<AskJanMitraResponse>("/ask-janmitra/image", { method: "POST", token, formData: form });
  },

  // The voice-to-voice assistant turn ("Mic 2") -- one or more recorded audio segments (see
  // lib/useAudioRecorder.ts, the same chunked-recording hook the complaint-creation voice flow
  // already uses) in, a real transcript + real spoken answer out. `image` is optional (a
  // combined voice+image turn), matching askJanMitraWithImage()'s same file-attach shape.
  askJanMitraVoice: (
    token: string,
    body: {
      language: string;
      latitude?: number | null;
      longitude?: number | null;
      location_text?: string | null;
      conversation_history?: AskJanMitraConversationTurn[];
      audioSegments: Blob[];
      image?: File | null;
    }
  ) => {
    const form = new FormData();
    form.append("language", body.language);
    if (body.latitude != null) form.append("latitude", String(body.latitude));
    if (body.longitude != null) form.append("longitude", String(body.longitude));
    if (body.location_text) form.append("location_text", body.location_text);
    form.append("conversation_history", JSON.stringify(body.conversation_history ?? []));
    body.audioSegments.forEach((segment, i) => form.append("audio", segment, `segment_${i}.webm`));
    if (body.image) form.append("image", body.image);
    return request<AskVoiceResponse>("/ask-janmitra/voice", { method: "POST", token, formData: form });
  },

  photoUrl: (filename: string) => `${API_URL}/uploads/${filename}`,
};

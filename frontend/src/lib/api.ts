import type {
  AuthMessage,
  AuthSession,
  TranscriptRead,
  TranscriptionJob,
  TranscriptionJobList,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const data = (await response.json()) as { detail?: string; message?: string };
      message = data.detail ?? data.message ?? message;
    } catch {
      // Ignore JSON parsing errors and use the response status text.
    }
    raiseApiError(message, response.status);
  }

  return (await response.json()) as T;
}

function raiseApiError(message: string, status: number): never {
  throw new ApiError(message, status);
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export function login(payload: { email: string; password: string }): Promise<AuthSession> {
  return request<AuthSession>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function register(payload: {
  email: string;
  given_name: string;
  last_name: string;
  password: string;
}): Promise<AuthSession["user"]> {
  return request<AuthSession["user"]>("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export function logout(): Promise<AuthMessage> {
  return request<AuthMessage>("/auth/logout", {
    method: "POST",
  });
}

export async function uploadTranscription(payload: {
  file: File;
  language?: string;
}): Promise<TranscriptionJob> {
  const formData = new FormData();
  formData.append("file", payload.file);
  if (payload.language) {
    formData.append("language", payload.language);
  }

  return request<TranscriptionJob>("/transcriptions/upload", {
    method: "POST",
    body: formData,
  });
}

export function listTranscriptions(): Promise<TranscriptionJobList> {
  return request<TranscriptionJobList>("/transcriptions");
}

export function getTranscription(jobId: number): Promise<TranscriptionJob> {
  return request<TranscriptionJob>(`/transcriptions/${jobId}`);
}

export function getTranscript(jobId: number): Promise<TranscriptRead> {
  return request<TranscriptRead>(`/transcriptions/${jobId}/result`);
}

export function deleteTranscription(jobId: number): Promise<AuthMessage> {
  return request<AuthMessage>(`/transcriptions/${jobId}`, {
    method: "DELETE",
  });
}

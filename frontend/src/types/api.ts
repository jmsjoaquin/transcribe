export type JobStatus = "pending" | "processing" | "completed" | "failed";

export interface UserRead {
  id: number;
  email: string;
  given_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthSession {
  message: string;
  user: UserRead;
}

export interface AuthMessage {
  message: string;
}

export interface TranscriptionJob {
  id: number;
  status: JobStatus;
  source_filename: string;
  language: string | null;
  model_name: string | null;
  duration_seconds: string | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  transcript_available: boolean;
}

export interface TranscriptionJobList {
  jobs: TranscriptionJob[];
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface TranscriptRead {
  job_id: number;
  status: JobStatus;
  full_text: string;
  segments_json: TranscriptSegment[] | null;
  confidence: number | null;
  created_at: string;
}

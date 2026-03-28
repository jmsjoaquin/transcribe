"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { getApiBaseUrl, getTranscript, getTranscription } from "@/lib/api";

function StatusPill({ status }: { status: string }) {
  return <span className={`pill${status === "failed" ? " failed" : ""}`}>{status}</span>;
}

export function JobDetail({ jobId }: { jobId: number }) {
  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getTranscription(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 3000;
    },
  });

  const transcriptQuery = useQuery({
    queryKey: ["transcript", jobId],
    queryFn: () => getTranscript(jobId),
    enabled: jobQuery.data?.status === "completed",
  });

  const downloadBase = `${getApiBaseUrl()}/transcriptions/${jobId}/download`;

  return (
    <div className="grid">
      <div className="panel stack">
        <div className="actions">
          <Link className="button-secondary" href="/dashboard">
            Back to Dashboard
          </Link>
          {jobQuery.data ? <StatusPill status={jobQuery.data.status} /> : null}
        </div>

        {jobQuery.isLoading ? <p className="muted">Loading job...</p> : null}
        {jobQuery.isError ? <p className="muted">{jobQuery.error.message}</p> : null}

        {jobQuery.data ? (
          <>
            <h1>{jobQuery.data.source_filename}</h1>
            <p className="muted">
              Language {jobQuery.data.language ?? "auto"} • Created{" "}
              {new Date(jobQuery.data.created_at).toLocaleString()}
            </p>
            {jobQuery.data.error_message ? (
              <p className="muted">{jobQuery.data.error_message}</p>
            ) : null}
            <div className="actions">
              <a className="button-secondary" href={`${downloadBase}?format=txt`}>
                Download TXT
              </a>
              <a className="button-secondary" href={`${downloadBase}?format=json`}>
                Download JSON
              </a>
            </div>
          </>
        ) : null}
      </div>

      <div className="panel stack">
        <span className="pill">Transcript</span>
        {transcriptQuery.isLoading ? <p className="muted">Waiting for transcript...</p> : null}
        {transcriptQuery.isError ? <p className="muted">{transcriptQuery.error.message}</p> : null}
        {transcriptQuery.data ? (
          <>
            <div className="transcript">{transcriptQuery.data.full_text}</div>
            {transcriptQuery.data.segments_json?.length ? (
              <div className="stack">
                <h3>Segments</h3>
                {transcriptQuery.data.segments_json.map((segment) => (
                  <div className="job-card" key={`${segment.start}-${segment.end}`}>
                    <strong>
                      {segment.start.toFixed(2)}s - {segment.end.toFixed(2)}s
                    </strong>
                    <div className="small">{segment.text}</div>
                  </div>
                ))}
              </div>
            ) : null}
          </>
        ) : (
          <p className="muted">
            Transcript data appears here once the worker completes the job.
          </p>
        )}
      </div>
    </div>
  );
}

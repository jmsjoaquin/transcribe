"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { deleteTranscription, listTranscriptions, logout } from "@/lib/api";

function StatusPill({ status }: { status: string }) {
  return <span className={`pill${status === "failed" ? " failed" : ""}`}>{status}</span>;
}

export function JobsList() {
  const queryClient = useQueryClient();

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: listTranscriptions,
    refetchInterval: 5000,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTranscription,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: async () => {
      await queryClient.clear();
    },
  });

  return (
    <div className="panel stack">
      <div className="actions">
        <span className="pill">Jobs</span>
        <button
          className="button-secondary"
          type="button"
          onClick={() => {
            void jobsQuery.refetch();
          }}
        >
          Refresh
        </button>
        <button
          className="button-secondary"
          type="button"
          onClick={() => {
            void logoutMutation.mutateAsync();
          }}
        >
          Logout
        </button>
      </div>

      {jobsQuery.isLoading ? <p className="muted">Loading jobs...</p> : null}
      {jobsQuery.isError ? <p className="muted">{jobsQuery.error.message}</p> : null}

      <div className="list">
        {jobsQuery.data?.jobs.length ? null : <p className="muted">No jobs yet.</p>}

        {jobsQuery.data?.jobs.map((job) => (
          <article className="job-card" key={job.id}>
            <div className="actions">
              <StatusPill status={job.status} />
              <span className="small muted">Job #{job.id}</span>
            </div>

            <div className="stack">
              <h3>{job.source_filename}</h3>
              <p className="small muted">
                Created {new Date(job.created_at).toLocaleString()} • Language{" "}
                {job.language ?? "auto"}
              </p>
              {job.error_message ? <p className="small muted">{job.error_message}</p> : null}
            </div>

            <div className="actions">
              <Link className="button" href={`/jobs/${job.id}`}>
                Open Job
              </Link>
              <button
                className="button-danger"
                type="button"
                onClick={() => {
                  void deleteMutation.mutateAsync(job.id);
                }}
              >
                Delete
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

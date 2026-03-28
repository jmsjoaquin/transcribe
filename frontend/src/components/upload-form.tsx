"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { uploadTranscription } from "@/lib/api";

export function UploadForm() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: uploadTranscription,
    onSuccess: async (job) => {
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
      router.push(`/jobs/${job.id}`);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  return (
    <div className="panel stack">
      <div className="stack">
        <span className="pill">Upload</span>
        <h2>Start a transcription job</h2>
        <p className="muted">
          Upload one file, enqueue it, and let the worker process it asynchronously.
        </p>
      </div>

      <form
        className="stack"
        onSubmit={async (event) => {
          event.preventDefault();
          setError(null);

          const formData = new FormData(event.currentTarget);
          const file = formData.get("file");
          const language = String(formData.get("language") ?? "").trim();

          if (!(file instanceof File) || file.size === 0) {
            setError("Choose an audio or video file first.");
            return;
          }

          await mutation.mutateAsync({
            file,
            language: language || undefined,
          });
        }}
      >
        <label className="field">
          <span>Media file</span>
          <input name="file" type="file" accept="audio/*,video/*" required />
        </label>

        <label className="field">
          <span>Language hint</span>
          <input name="language" placeholder="en" />
        </label>

        {error ? <p className="muted">{error}</p> : null}

        <div className="actions">
          <button className="button" type="submit" disabled={mutation.isPending}>
            Upload and Queue
          </button>
        </div>
      </form>
    </div>
  );
}

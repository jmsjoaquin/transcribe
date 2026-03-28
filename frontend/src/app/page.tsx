import Link from "next/link";

export default function HomePage() {
  return (
    <main className="shell grid">
      <section className="hero">
        <span className="pill">Local-first transcription</span>
        <h1>Queue long audio. Let the worker do the heavy lifting.</h1>
        <p>
          This frontend scaffold targets the current FastAPI + Redis + worker backend already
          running in the repository. Use it as the starting point for login, uploads, job
          tracking, and transcript review.
        </p>
        <div className="actions">
          <Link className="button" href="/login">
            Open Auth
          </Link>
          <Link className="button-secondary" href="/dashboard">
            Open Dashboard
          </Link>
        </div>
      </section>

      <section className="grid two">
        <article className="panel stack">
          <span className="pill">Current flow</span>
          <h2>Backend contract already wired</h2>
          <p className="muted">
            The dashboard expects cookie auth, `POST /transcriptions/upload`, polling on
            `GET /transcriptions/{'{job_id}'}`, and transcript retrieval/download endpoints.
          </p>
        </article>

        <article className="panel stack">
          <span className="pill">Target worker</span>
          <h2>Mac for dev, Windows RTX for throughput</h2>
          <p className="muted">
            The current local runbook supports macOS smoke tests with `SimpleWorker`, while the
            architecture stays compatible with a dedicated Windows GPU worker.
          </p>
        </article>
      </section>
    </main>
  );
}

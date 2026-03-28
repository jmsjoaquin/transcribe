import Link from "next/link";

import { JobsList } from "@/components/jobs-list";
import { UploadForm } from "@/components/upload-form";

export default function DashboardPage() {
  return (
    <main className="shell grid">
      <section className="hero">
        <span className="pill">Dashboard</span>
        <h1>Upload once. Poll until it is done.</h1>
        <p>
          This page maps directly to the current MVP backend: upload, list jobs, delete jobs,
          and jump into per-job transcript detail.
        </p>
        <div className="actions">
          <Link className="button-secondary" href="/login">
            Auth Screen
          </Link>
        </div>
      </section>

      <div className="grid two">
        <UploadForm />
        <JobsList />
      </div>
    </main>
  );
}

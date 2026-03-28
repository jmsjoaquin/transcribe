import { JobDetail } from "@/components/job-detail";

export default async function JobDetailPage({
  params,
}: {
  params: { jobId: string };
}) {
  const { jobId } = params;
  const numericJobId = Number(jobId);

  return (
    <main className="shell">
      <JobDetail jobId={numericJobId} />
    </main>
  );
}

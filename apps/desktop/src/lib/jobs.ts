import { type JobView, getJob } from './api';

const POLL_MS = 400;
const DEADLINE_MS = 120_000;

/** Poll GET /jobs/{id} through the generated client until the worker finishes. */
export async function pollJob(jobId: string, onPercent?: (percent: number) => void): Promise<JobView> {
  const deadline = Date.now() + DEADLINE_MS;
  while (Date.now() < deadline) {
    const { data, error } = await getJob({ path: { job_id: jobId } });
    if (error || !data) {
      throw new Error('وضعیت کار خوانده نشد');
    }
    onPercent?.(data.percent);
    if (data.status === 'done' || data.status === 'error' || data.status === 'cancelled') {
      return data;
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_MS));
  }
  throw new Error('زمان کار تمام شد');
}

export function jobFailure(error: unknown, status: number | undefined, fallback: string): string {
  if (error && typeof error === 'object' && 'error' in error) {
    const message = (error as { error?: unknown }).error;
    if (typeof message === 'string' && message) return message;
  }
  return status ? `${fallback} (${status})` : fallback;
}

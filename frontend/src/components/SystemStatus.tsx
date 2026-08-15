"use client";

import { useEffect, useState } from "react";

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

type SchedulerJob = {
  id: string;
  next_run_time?: string | null;
};

type SchedulerResult = {
  topic?: string;
  status?: string;
  package_id?: string | null;
  message?: string | null;
};

type SchedulerStatus = {
  running?: boolean;
  timezone?: string;
  active_pipelines?: string[];
  last_run_started_at?: string | null;
  last_run_finished_at?: string | null;
  last_run_status?: string | null;
  last_run_results?: SchedulerResult[];
  jobs?: SchedulerJob[];
};

export default function SystemStatus() {
  const [status, setStatus] =
    useState<SchedulerStatus | null>(null);

  const [error, setError] =
    useState(false);

  useEffect(() => {
    async function loadStatus() {
      try {
        const response = await fetch(
          `${API}/scheduler/status`
        );

        if (!response.ok) {
          throw new Error(
            `Status request failed: ${response.status}`
          );
        }

        const result =
          await response.json();

        setStatus(result);
        setError(false);
      } catch (statusError) {
        console.error(
          "Could not load system status:",
          statusError
        );

        setError(true);
      }
    }

    loadStatus();

    const interval =
      window.setInterval(
        loadStatus,
        30000
      );

    return () =>
      window.clearInterval(
        interval
      );
  }, []);

  const nextRun =
    status?.jobs?.[0]?.next_run_time;

  return (
    <section className="mt-8 rounded-[28px] border border-[#E4DDD2] bg-[#FFFDF9] p-6 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[4px] text-[#927F68]">
            System Status
          </p>

          <h2
            className="mt-2 text-3xl text-[#171615]"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            Production health
          </h2>

          <p className="mt-2 text-sm text-[#746B62]">
            Scheduler and daily pipeline status.
          </p>
        </div>

        <span className="w-fit rounded-full border border-[#DDD5C9] bg-white px-4 py-2 text-xs font-semibold text-[#675F57]">
          {status?.timezone ||
            "Asia/Kolkata"}
        </span>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatusCard
          label="Scheduler"
          value={
            error
              ? "Unavailable"
              : status?.running
              ? "Running"
              : "Stopped"
          }
        />

        <StatusCard
          label="Active Pipeline"
          value={
            status?.active_pipelines?.length
              ? status.active_pipelines.join(
                  ", "
                )
              : "Idle"
          }
        />

        <StatusCard
          label="Last Daily Run"
          value={
            status?.last_run_status ||
            "Not recorded"
          }
        />

        <StatusCard
          label="Next Run"
          value={
            nextRun
              ? new Date(
                  nextRun
                ).toLocaleString()
              : "Not scheduled"
          }
        />
      </div>

      {status?.last_run_results &&
        status.last_run_results.length > 0 && (
          <div className="mt-5 flex flex-wrap gap-2">
            {status.last_run_results.map(
              (result, index) => (
                <span
                  key={`${result.topic}-${index}`}
                  className="rounded-full border border-[#DDD5C9] bg-[#F6F2EA] px-4 py-2 text-xs font-semibold text-[#665D54]"
                >
                  {result.topic?.toUpperCase() ||
                    "PIPELINE"}
                  {" · "}
                  {result.status ||
                    "unknown"}
                </span>
              )
            )}
          </div>
        )}
    </section>
  );
}

function StatusCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[20px] border border-[#E6DED3] bg-white p-5">
      <p className="text-[10px] font-bold uppercase tracking-[3px] text-[#998875]">
        {label}
      </p>

      <p className="mt-3 text-sm font-semibold text-[#25211D]">
        {value}
      </p>
    </div>
  );
}
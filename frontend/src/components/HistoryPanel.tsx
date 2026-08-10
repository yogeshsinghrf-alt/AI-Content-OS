"use client";

import { useState } from "react";

type HistoryItem = {
  filename: string;
  topic?: string;
  title?: string;
  source?: string;
};

type HistoryPanelProps = {
  history: HistoryItem[];
  onLoadHistory: (filename: string) => void;
  onDeleteHistory: (filename: string) => void;
};

export default function HistoryPanel({
  history,
  onLoadHistory,
  onDeleteHistory,
}: HistoryPanelProps) {
  const [showAll, setShowAll] = useState(false);

  if (history.length === 0) {
    return null;
  }

  const visibleHistory = showAll
    ? history
    : history.slice(0, 3);

  return (
    <section className="rounded-[28px] border border-[#E4DDD2] bg-[#FFFDF9] p-6 shadow-sm">

      {/* Header */}
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#928575]">
            Content Library
          </p>

          <h2
            className="mt-2 text-3xl text-[#171615]"
            style={{
              fontFamily: "Instrument Serif",
            }}
          >
            Recent Content
          </h2>

          <p className="mt-1 text-sm text-[#776E65]">
            Reopen previously generated content packages.
          </p>
        </div>

        <span className="rounded-full border border-[#DDD5C9] bg-white px-4 py-2 text-xs font-semibold text-[#6C635A]">
          {history.length} saved
        </span>
      </div>

      {/* History items */}
      <div className="grid gap-3 lg:grid-cols-3">
        {visibleHistory.map((item) => (
          <div
            key={item.filename}
            onClick={() =>
              onLoadHistory(item.filename)
            }
            className="group cursor-pointer rounded-[20px] border border-[#E5DED3] bg-white p-5 transition hover:-translate-y-0.5 hover:border-[#CFC5B7] hover:shadow-md"
          >
            <div className="flex items-start justify-between gap-3">
              <span className="rounded-full bg-[#F3EFE7] px-3 py-1 text-[10px] font-bold uppercase tracking-[2px] text-[#817466]">
                {item.topic || "Content"}
              </span>

              <button
                type="button"
                aria-label="Delete history item"
                onClick={(event) => {
                  event.stopPropagation();
                  onDeleteHistory(
                    item.filename
                  );
                }}
                className="rounded-full px-2 py-1 text-sm text-[#A49A8E] transition hover:bg-[#F8E9E7] hover:text-[#A84C43]"
              >
                ×
              </button>
            </div>

            <h3 className="mt-4 line-clamp-2 min-h-[48px] text-base font-bold leading-6 text-[#24211E]">
              {item.title ||
                "Generated Content"}
            </h3>

            <div className="mt-5 flex items-center justify-between border-t border-[#EEE8DF] pt-4">
              <p className="truncate pr-3 text-xs text-[#8A8178]">
                {item.source ||
                  "AI Content OS"}
              </p>

              <span className="shrink-0 text-xs font-semibold text-[#5E554C] transition group-hover:translate-x-1">
                Open →
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Show all / collapse */}
      {history.length > 3 && (
        <div className="mt-5 flex justify-center border-t border-[#EEE8DF] pt-5">
          <button
            type="button"
            onClick={() =>
              setShowAll(
                (current) => !current
              )
            }
            className="rounded-full border border-[#D6CEC2] bg-white px-5 py-2.5 text-sm font-semibold text-[#514A43] transition hover:bg-[#F5F1E9]"
          >
            {showAll
              ? "Show Less"
              : `View All History (${history.length})`}
          </button>
        </div>
      )}
    </section>
  );
}
"use client";

type ToolbarProps = {
  topic: string;
  sourceMode:
    | "industry"
    | "company";
  loading: boolean;

  onTopicChange: (
    topic: string
  ) => void;

  onGenerate: () => void;
  onCopyAll: () => void;
  onExportPDF: () => void;
  onExportPNG: () => void;
};

export default function Toolbar({
  topic,
  sourceMode,
  loading,
  onTopicChange,
  onGenerate,
  onCopyAll,
  onExportPDF,
  onExportPNG,
}: ToolbarProps) {
  return (
    <div className="mb-8">
      {/* -----------------------------------------
          EXPORT / COPY ACTIONS
      ----------------------------------------- */}
      <div className="mb-6 flex flex-wrap gap-4">
        <button
          type="button"
          onClick={onCopyAll}
          className="rounded-2xl bg-[#171615] px-5 py-3 text-white shadow-sm"
        >
          📋 Copy All
        </button>

        <button
          type="button"
          onClick={onExportPDF}
          className="rounded-2xl border border-[#E7E1D8] bg-[#FFFDF8] px-5 py-3 shadow-sm"
        >
          📄 Export PDF
        </button>

        <button
          type="button"
          onClick={onExportPNG}
          className="rounded-2xl border border-[#E7E1D8] bg-[#FFFDF8] px-5 py-3 shadow-sm"
        >
          🖼 Export PNG
        </button>
      </div>

      {/* -----------------------------------------
          GENERATION CONTROLS
      ----------------------------------------- */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Topic selection is relevant only
            for Industry Intelligence mode */}
        {sourceMode ===
          "industry" && (
          <select
            value={topic}
            onChange={(event) =>
              onTopicChange(
                event.target.value
              )
            }
            className="rounded-xl border border-[#DED7CC] bg-white px-5 py-3 text-sm font-semibold text-[#5F574F] outline-none"
          >
            <option value="ai">
              AI
            </option>

            <option value="telecom">
              Telecom
            </option>

            <option value="marketing">
              Marketing
            </option>
          </select>
        )}

        <button
          type="button"
          onClick={onGenerate}
          disabled={loading}
          className="rounded-xl bg-[#171615] px-6 py-3 font-semibold text-white shadow hover:bg-[#2B2927] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />

              Generating...
            </span>
          ) : sourceMode ===
            "company" ? (
            "Generate Company Content"
          ) : (
            "Generate Content"
          )}
        </button>
      </div>
    </div>
  );
}
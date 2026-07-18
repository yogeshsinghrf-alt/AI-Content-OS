type ToolbarProps = {
  topic: string;
  loading: boolean;
  onTopicChange: (topic: string) => void;
  onGenerate: () => void;
  onCopyAll: () => void;
  onExportPDF: () => void;
};

export default function Toolbar({
  topic,
  loading,
  onTopicChange,
  onGenerate,
  onCopyAll,
  onExportPDF,
}: ToolbarProps) {
  return (
    <div className="mb-8">
      <div className="flex gap-4 mb-6 flex-wrap">
        <button
          onClick={onCopyAll}
          className="bg-[#171615] text-white px-5 py-3 rounded-2xl shadow-sm"
        >
          📋 Copy All
        </button>

        <button
          onClick={onExportPDF}
          className="bg-[#FFFDF8] border border-[#E7E1D8] px-5 py-3 rounded-2xl shadow-sm"
        >
          📄 Export PDF
        </button>

        <button
          disabled
          title="PNG export will be added later"
          className="bg-[#FFFDF8] border border-[#E7E1D8] px-5 py-3 rounded-2xl shadow-sm opacity-50 cursor-not-allowed"
        >
          🖼 Export PNG
        </button>
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <select
          value={topic}
          onChange={(event) => onTopicChange(event.target.value)}
          className="bg-[#FFFDF8] border border-[#E7E1D8] rounded-2xl px-5 py-3 shadow-sm"
        >
          <option value="ai">AI</option>
          <option value="telecom">Telecom</option>
          <option value="marketing">Marketing</option>
        </select>

        <button
          onClick={onGenerate}
          disabled={loading}
          className="bg-[#171615] hover:bg-[#2B2927] disabled:opacity-60 text-white px-6 py-3 rounded-xl font-semibold shadow"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
              Generating...
            </span>
          ) : (
            "Generate Content"
          )}
        </button>
      </div>
    </div>
  );
}
type SourcePanelProps = {
  sources?: string[];
};

export default function SourcePanel({
  sources = [],
}: SourcePanelProps) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow p-6 mt-8 mb-8 border">
      <h3 className="text-lg font-bold mb-4">
        Sources Active
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {sources.map((source) => (
          <div
            key={source}
            className="flex items-center gap-2 bg-slate-50 border rounded-lg px-4 py-3"
          >
            <span className="text-green-600 font-bold">
              ✓
            </span>

            <span className="text-sm">
              {source}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
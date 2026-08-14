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
    <div className="mt-8 mb-8 rounded-2xl border bg-white p-6 shadow">
      <div className="mb-4">
        <h3 className="text-lg font-bold">
          Source Network
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Sources contributing to this content package
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {sources.map((source) => (
          <div
            key={source}
            className="flex items-center gap-3 rounded-lg border bg-slate-50 px-4 py-3"
          >
            <span className="h-2 w-2 shrink-0 rounded-full bg-emerald-500" />

            <span className="text-sm">
              {source}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
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
  if (history.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 mb-8 bg-[#FFFDF8] rounded-[32px] border border-[#E7E1D8] p-8 shadow-sm">
      <p className="text-xs uppercase tracking-[4px] text-[#8B8175] mb-4">
        History
      </p>

      <h2 className="text-3xl font-black mb-6">
        Recent Content
      </h2>

      <div className="space-y-4">
        {history.slice(0, 5).map((item) => (
          <div
            key={item.filename}
            onClick={() => onLoadHistory(item.filename)}
            className="border border-[#E7E1D8] rounded-2xl p-4 bg-white cursor-pointer hover:shadow-md transition"
          >
            <p className="text-sm text-[#8B8175] uppercase">
              {item.topic}
            </p>

            <h3 className="font-bold text-lg">
              {item.title}
            </h3>

            <p className="text-sm text-slate-500">
              {item.source}
            </p>

            <button
              onClick={(event) => {
                event.stopPropagation();
                onDeleteHistory(item.filename);
              }}
              className="mt-3 text-red-600 text-sm hover:underline"
            >
              🗑 Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
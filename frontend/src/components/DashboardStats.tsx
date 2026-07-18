type DashboardStatsProps = {
  topic: string;
};

export default function DashboardStats({
  topic,
}: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-[#FFFDF8] rounded-[28px] border border-[#E7E1D8] p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[3px] text-[#8B8175]">
          Selected Topic
        </p>

        <p className="text-5xl font-black text-[#171615] uppercase">
          {topic}
        </p>
      </div>

      <div className="bg-[#FFFDF8] rounded-[28px] border border-[#E7E1D8] p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[3px] text-[#8B8175]">
          Content Outputs
        </p>

        <p className="text-4xl font-black text-[#171615]">
          6
        </p>
      </div>

      <div className="bg-[#FFFDF8] rounded-[28px] border border-[#E7E1D8] p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[3px] text-[#8B8175]">
          AI Engine
        </p>

        <p className="text-4xl font-black text-[#171615]">
          Gemini
        </p>
      </div>
    </div>
  );
}
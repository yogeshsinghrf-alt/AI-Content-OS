type DashboardStatsProps = {
  topic: string;
};

export default function DashboardStats({
  topic,
}: DashboardStatsProps) {
  const stats = [
    {
      eyebrow: "Selected Topic",
      value: topic.toUpperCase(),
      detail: "Live industry intelligence",
      number: "01",
    },
    {
      eyebrow: "Story Outputs",
      value: "8",
      detail: "Posts · Visuals · Carousel · Infographic",
      number: "02",
    },
    {
      eyebrow: "AI Engine",
      value: "Gemini",
      detail: "Research-to-content generation",
      number: "03",
    },
    {
      eyebrow: "Delivery",
      value: "Automated",
      detail: "Scheduled content workflow",
      number: "04",
    },
  ];

  return (
    <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <div
          key={stat.eyebrow}
          className="group relative overflow-hidden rounded-[26px] border border-[#E3DCD1] bg-[#FFFDF8] p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
        >
          {/* Number */}
          <div className="flex items-start justify-between">
            <p className="text-[10px] font-bold uppercase tracking-[3px] text-[#8B8175]">
              {stat.eyebrow}
            </p>

            <span
              className="text-2xl leading-none text-[#D1C5B5]"
              style={{
                fontFamily: "Instrument Serif",
              }}
            >
              {stat.number}
            </span>
          </div>

          {/* Main value */}
          <p
            className={`mt-7 leading-none text-[#171615] ${
              stat.value.length > 10
                ? "text-3xl"
                : "text-4xl"
            }`}
            style={{
              fontFamily: "Instrument Serif",
            }}
          >
            {stat.value}
          </p>

          {/* Description */}
          <p className="mt-3 min-h-[36px] text-xs leading-5 text-[#81776D]">
            {stat.detail}
          </p>

          {/* Accent */}
          <div className="mt-5 h-[2px] w-10 bg-[#B8A58D] transition-all duration-300 group-hover:w-20" />
        </div>
      ))}
    </section>
  );
}
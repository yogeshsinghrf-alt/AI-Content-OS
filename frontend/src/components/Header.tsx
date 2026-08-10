export default function Header() {
  return (
    <section className="relative overflow-hidden rounded-[32px] border border-[#E3DCD1] bg-[#FFFDF8] px-8 py-10 shadow-sm lg:px-10 lg:py-12">

      {/* Soft decorative background */}
      <div className="pointer-events-none absolute -right-20 -top-28 h-72 w-72 rounded-full bg-[#E2E9E1]/70 blur-3xl" />

      <div className="pointer-events-none absolute -bottom-28 left-[30%] h-64 w-64 rounded-full bg-[#EEE1CF]/70 blur-3xl" />

      <div className="relative">

        {/* Eyebrow */}
        <div className="mb-6 flex flex-wrap items-center gap-3">

          <span className="rounded-full border border-[#D8D0C4] bg-white px-4 py-2 text-[10px] font-bold uppercase tracking-[3px] text-[#756A5E]">
            AI Social Content Studio
          </span>

          <span className="rounded-full bg-[#E7EEE8] px-4 py-2 text-[10px] font-bold uppercase tracking-[2px] text-[#536158]">
            Live News → Content
          </span>

        </div>

        {/* Main title */}
        <h1
          className="max-w-4xl text-5xl leading-[0.95] tracking-tight text-[#171615] md:text-6xl lg:text-7xl"
          style={{
            fontFamily: "Instrument Serif",
          }}
        >
          Turn live industry news into
          <span className="text-[#88745E]">
            {" "}publication-ready content.
          </span>
        </h1>

        {/* Description */}
        <p className="mt-6 max-w-3xl text-base leading-7 text-[#6F675E] md:text-lg">
          AI Content OS discovers current stories and transforms
          them into platform-specific social posts, editorial
          visuals, carousels and infographics for AI, Telecom
          and Marketing.
        </p>

        {/* Product capabilities */}
        <div className="mt-8 flex flex-wrap gap-2">

          {[
            "AI · Telecom · Marketing",
            "6 Creative Formats",
            "AI Visual Generation",
            "Anti-Repeat Selection",
            "PNG + PDF Export",
            "Scheduled Delivery",
          ].map((feature) => (
            <span
              key={feature}
              className="rounded-full border border-[#DDD5C9] bg-white/80 px-4 py-2 text-xs font-semibold text-[#625A52]"
            >
              {feature}
            </span>
          ))}

        </div>

        {/* Product identity */}
        <div className="mt-9 flex items-center gap-4 border-t border-[#E4DDD2] pt-6">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#171615] text-sm font-bold text-white">
            AI
          </div>

          <div>
            <p className="text-sm font-bold text-[#292622]">
              AI Content OS
            </p>

            <p className="mt-0.5 text-xs text-[#8A8178]">
              Intelligent multi-platform content automation
            </p>
          </div>

        </div>

      </div>
    </section>
  );
}
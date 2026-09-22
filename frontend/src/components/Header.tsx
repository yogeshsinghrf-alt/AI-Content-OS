"use client";

export default function Header() {
  async function handleLogout() {
    try {
      const response = await fetch("/api/logout", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Logout failed");
      }

      window.location.href = "/login";
    } catch (error) {
      console.error(
        "Logout failed:",
        error
      );

      alert(
        "Could not log out. Please try again."
      );
    }
  }

  return (
    <section className="relative overflow-hidden rounded-[32px] border border-[#E3D8CA] bg-[#F7F3EB] px-8 py-10 shadow-sm lg:px-10 lg:py-12">

      {/* Soft premium bronze background details */}
      <div className="pointer-events-none absolute -right-20 -top-28 h-72 w-72 rounded-full bg-[#A67C52]/10 blur-3xl" />

      <div className="pointer-events-none absolute -bottom-28 left-[28%] h-64 w-64 rounded-full bg-[#C9A982]/10 blur-3xl" />

      <div className="relative">

        {/* Top row */}
        <div className="mb-7 flex items-start justify-between gap-4">

          <div className="flex flex-wrap items-center gap-3">

            {/* ELANROVE brand */}
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-[#A67C52]/50 bg-white/70 text-sm font-bold text-[#A67C52]">
                E
              </div>

              <span className="text-[12px] font-bold uppercase tracking-[4px] text-[#A67C52]">
                ELANROVE
              </span>
            </div>

            <span className="hidden h-5 w-px bg-[#D9C9B8] sm:block" />

            <span className="rounded-full border border-[#DCCDBD] bg-white/70 px-4 py-2 text-[10px] font-bold uppercase tracking-[2.5px] text-[#786B5F]">
              AI Content OS
            </span>

            <span className="rounded-full border border-[#D9C4AE] bg-[#A67C52]/8 px-4 py-2 text-[10px] font-bold uppercase tracking-[2px] text-[#8D6845]">
              Intelligence → Communications
            </span>

          </div>

          {/* Logout */}
          <button
            type="button"
            onClick={handleLogout}
            className="shrink-0 rounded-full border border-[#D8CCBE] bg-white/80 px-4 py-2 text-[11px] font-semibold text-[#625A52] transition hover:border-[#A67C52]/50 hover:text-[#A67C52]"
          >
            Log out
          </button>

        </div>

        {/* Main title */}
        <h1
          className="max-w-5xl text-5xl leading-[0.95] tracking-tight text-[#181716] md:text-6xl lg:text-7xl"
          style={{
            fontFamily:
              "Instrument Serif",
          }}
        >
          Turn trusted information into
          <span className="text-[#A67C52]">
            {" "}
            publication-ready communications.
          </span>
        </h1>

        {/* Description */}
        <p className="mt-6 max-w-3xl text-base leading-7 text-[#6F675E] md:text-lg">
          AI Content OS transforms live
          industry intelligence or approved
          company announcements into
          platform-specific social content,
          branded visuals, carousels and
          infographics.
        </p>

        {/* Product capabilities */}
        <div className="mt-8 flex flex-wrap gap-2">
          {[
            "Industry Intelligence",
            "Company Newsroom",
            "6 Social Variants",
            "AI Visual Generation",
            "Carousel + Infographic",
            "PNG + PDF Export",
          ].map((feature) => (
            <span
              key={feature}
              className="rounded-full border border-[#DED2C5] bg-white/75 px-4 py-2 text-xs font-semibold text-[#625A52]"
            >
              {feature}
            </span>
          ))}
        </div>

        {/* Product identity */}
        <div className="mt-9 flex items-center gap-4 border-t border-[#DED3C7] pt-6">

          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-[#A67C52]/50 bg-[#A67C52] text-base font-bold text-[#F7F3EB] shadow-sm">
            E
          </div>

          <div>
            <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <p className="text-sm font-bold uppercase tracking-[3px] text-[#A67C52]">
                ELANROVE
              </p>

              <span className="text-xs text-[#B4A79A]">
                /
              </span>

              <p className="text-sm font-semibold text-[#292622]">
                AI Content OS
              </p>
            </div>

            <p className="mt-1 text-xs text-[#8A8178]">
              Source-to-communications
              intelligence platform
            </p>
          </div>

        </div>

      </div>
    </section>
  );
}
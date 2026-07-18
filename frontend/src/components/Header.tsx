export default function Header() {
  return (
    <div className="mb-8 rounded-[32px] bg-[#FFFDF8] border border-[#E7E1D8] px-10 py-8 shadow-sm">
      <p className="text-xs tracking-[4px] uppercase text-[#8B8175] mb-4">
        AI Social Content Studio
      </p>

      <h1
        className="text-6xl font-black tracking-tight text-[#171615]"
        style={{ fontFamily: "Instrument Serif" }}
      >
        AI Content OS
      </h1>

      <p className="text-[#6F675E] mt-4 text-lg max-w-2xl">
        Generate editorial-style social content from live AI, telecom, and
        marketing news.
      </p>
    </div>
  );
}
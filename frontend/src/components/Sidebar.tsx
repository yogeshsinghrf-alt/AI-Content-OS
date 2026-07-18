type SidebarProps = {
  activeView: string;
  setActiveView: (view: string) => void;
};

export default function Sidebar({
  activeView,
  setActiveView,
}: SidebarProps) {
  const itemClass = (view: string) =>
    activeView === view
      ? "bg-[#171615] text-white rounded-2xl px-4 py-3 cursor-pointer"
      : "text-[#7B7269] px-4 py-3 hover:bg-[#F5F2EA] rounded-2xl cursor-pointer transition";

  return (
    <aside className="w-72 bg-[#FFFDF8] border-r border-[#E7E1D8] p-8 hidden lg:block">
      <h2
        className="text-4xl mb-10"
        style={{ fontFamily: "Instrument Serif" }}
      >
        AI Content OS
      </h2>

      <nav className="space-y-3">
        <div
          onClick={() => setActiveView("dashboard")}
          className={itemClass("dashboard")}
        >
          🏠 Dashboard
        </div>

        <div className={itemClass("visual-studio")}>
          🎨 Visual Studio
        </div>

        <div className={itemClass("content-library")}>
          📚 Content Library
        </div>

        <div
          onClick={() => setActiveView("history")}
          className={itemClass("history")}
        >
          🕒 History
        </div>

        <div className={itemClass("exports")}>
          📤 Exports
        </div>

        <div className={itemClass("settings")}>
          ⚙ Settings
        </div>
      </nav>
    </aside>
  );
}
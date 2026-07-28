"use client";

import { useState, useEffect } from "react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import Sidebar from "../components/Sidebar";
import HistoryPanel from "../components/HistoryPanel";
import DashboardStats from "../components/DashboardStats";
import Header from "../components/Header";
import Toolbar from "../components/Toolbar";
import SourcePanel from "../components/SourcePanel";
const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";
export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState("ai");
  const [history, setHistory] = useState<any[]>([]);
  const [activeView, setActiveView] = useState("dashboard");
  const [heroImage, setHeroImage] = useState("");
  const [historySearch, setHistorySearch] = useState("");
  const [historyTopic, setHistoryTopic] = useState("all");
  useEffect(() => {
  fetchHistory();
}, []);
  
async function fetchHistory() {
  const response = await fetch(`${API}/history/`);
  const result = await response.json();
  setHistory(result);
}
  async function loadHistory(filename: string) {
  const response = await fetch(
    `${API}/history/${filename}`
  );

  const result = await response.json();

  if (typeof result.content_package === "string") {
    try {
      result.content_package = JSON.parse(result.content_package);
    } catch {
      alert("Could not parse saved content.");
    }
  }

  setData(result);
  alert("History loaded.");
}
async function deleteHistory(filename: string) {
  await fetch(
    `${API}/history/${filename}`,
    {
      method: "DELETE",
    }
  );

  fetchHistory();
}
async function generateContent() {
    setLoading(true);

    const response = await fetch(
  `${API}/package/daily?topic=${topic}`
);

    const result = await response.json();

    if (
      typeof result.content_package === "string"
    ) {
      try {
        result.content_package = JSON.parse(
          result.content_package
        );
      } catch {}
    }

    setData(result);
    const imageResponse = await fetch(
  `${API}/image/generate?prompt=${encodeURIComponent(
    result.content_package.hero_image_prompt
  )}`
);

const imageData = await imageResponse.json();

setHeroImage(imageData.image_url);
    setLoading(false);
  }

  function copyText(text: string) {
    navigator.clipboard.writeText(text);
    alert("Copied!");
  }
function copyAllContent() {
  if (!data) return;

  navigator.clipboard.writeText(
    JSON.stringify(data.content_package, null, 2)
  );

  alert("All content copied.");
}

function exportPDF() {
  window.print();
}
const filteredHistory = history.filter((item) => {
  const matchesTopic =
    historyTopic === "all" || item.topic === historyTopic;

  const matchesSearch =
    item.title?.toLowerCase().includes(historySearch.toLowerCase()) ||
    item.source?.toLowerCase().includes(historySearch.toLowerCase());

  return matchesTopic && matchesSearch;
});
return (
    <main className="min-h-screen bg-[#F5F2EA] text-[#181716]">
      <div className="flex min-h-screen">
        <Sidebar
  activeView={activeView}
  setActiveView={setActiveView}
/>
    <div className="flex-1 p-8">
     {activeView === "history" && (
  <div className="bg-[#FFFDF8] rounded-[32px] border border-[#E7E1D8] p-8 shadow-sm">
    <p className="text-xs uppercase tracking-[4px] text-[#8B8175] mb-4">
      HISTORY
    </p>

    <h1
      className="text-5xl mb-8"
      style={{ fontFamily: "Instrument Serif" }}
    >
      Saved Content Packages
    </h1>

    <div className="space-y-4">
      {history.map((item, index) => (
        <div
          key={index}
          onClick={() => loadHistory(item.filename)}
          className="border border-[#E7E1D8] rounded-2xl p-5 bg-white cursor-pointer hover:shadow-md transition"
        >
          <p className="text-sm uppercase text-[#8B8175]">
            {item.topic}
          </p>

          <h3 className="font-bold text-lg">
            {item.title}
          </h3>

          <p className="text-sm text-slate-500">
            {item.source}
          </p>
          <div className="mt-3">
  <button
    onClick={(e) => {
      e.stopPropagation();
      deleteHistory(item.filename);
    }}
    className="text-red-600 text-sm hover:underline"
  >
    🗑 Delete
  </button>
         </div>
        </div>
      ))}
    </div>
  </div>
)}  
   <Header />

   <Toolbar
     topic={topic}
     loading={loading}
     onTopicChange={setTopic}
     onGenerate={generateContent}
     onCopyAll={copyAllContent}
     onExportPDF={() => window.print()}
   />

   <DashboardStats topic={topic} />
        
<HistoryPanel
  history={filteredHistory}
  onLoadHistory={loadHistory}
  onDeleteHistory={deleteHistory}
/>
        {data && (
  <div id="content-package">
  <SourcePanel sources={data.available_sources} />
            <div className="bg-white rounded-2xl shadow p-6 mt-8 mb-8">
              <p className="text-sm text-slate-500">
                {data.source}
              </p>

              <h2 className="text-2xl font-bold mt-2">
                {data.article_title}
              </h2>

              <a
                href={data.article_link}
                target="_blank"
                className="text-blue-600 underline text-sm"
              >
                Read Original Article
              </a>
            </div>
           {data.content_package.editorial_headline && (
  <div className="rounded-[40px] bg-[#F8F6F1] border border-[#E7E1D8] p-12 mb-8 shadow-sm overflow-hidden">
    
    <div className="text-xs uppercase tracking-[4px] text-gray-500 mb-8">
      BUSINESS FRAMEWORK
    </div>

    <h1
  className="text-6xl leading-none font-black text-[#151515] max-w-3xl"
  style={{ fontFamily: "Instrument Serif" }}
>
  {data.content_package.editorial_headline}
</h1>

    <p className="text-2xl italic text-[#867B70] mt-6 max-w-2xl">
      {data.content_package.editorial_subtitle}
    </p>

  </div>
)}
            {data.content_package.hero_image_prompt && (
  <div className="bg-gradient-to-br from-amber-50 via-stone-50 to-emerald-50 rounded-3xl shadow p-8 border mb-8">
    <p className="text-sm font-semibold text-emerald-700 mb-2">
      AI Visual Direction
    </p>

    <h2 className="text-3xl font-bold text-slate-900 mb-4">
      Hero Image Concept
    </h2>

    <p className="text-slate-700 leading-7">
      {data.content_package.hero_image_prompt}
    </p>
  </div>
)}
       {data.content_package.quote_card && (
  <div className="bg-white rounded-3xl border p-10 mb-8 shadow-sm">

    <div className="text-5xl text-[#C9B08C] mb-6">
      ❝
    </div>

    <p
  className="text-3xl leading-relaxed text-gray-800"
  style={{ fontFamily: "Instrument Serif" }}
>
      {data.content_package.quote_card}
    </p>

  </div>
)}     
       {data.content_package.infographic_points && (
  <div className="bg-[#FBF9F4] rounded-3xl p-10 mb-8 border">

    <h2 className="text-2xl font-bold mb-8">
      Key Takeaways
    </h2>

    <div className="space-y-4">
      {data.content_package.infographic_points.map(
        (point: string, index: number) => (
          <div
            key={index}
            className="flex gap-4 items-center"
          >
            <div className="w-10 h-10 rounded-full bg-[#E6D9C5] flex items-center justify-center font-bold">
              {index + 1}
            </div>

            <span className="text-lg">
              {point}
            </span>
          </div>
        )
      )}
    </div>

  </div>
)}     <div className="mb-8">
  <p className="text-xs uppercase tracking-[4px] text-[#8B8175] mb-3">
    CONTENT OUTPUTS
  </p>

  <h2 className="text-4xl font-black text-[#171615]">
    Editorial Content Collection
  </h2>
</div>
<div className="mb-8">
  <p className="text-xs uppercase tracking-[4px] text-[#8B8175] mb-3">
    VISUAL CONTENT MODES
  </p>

  <h2 className="text-4xl font-black text-[#171615]">
    Design Concepts
  </h2>
</div>
<div className="mb-8">
  <p className="text-xs uppercase tracking-[4px] text-[#8B8175] mb-3">
    VISUAL GALLERY
  </p>

  <h2 className="text-4xl font-black text-[#171615]">
    Image & Infographic Directions
  </h2>
</div>

{heroImage && (
  <div className="mb-8">
    <img
      src={heroImage}
      className="rounded-[32px] shadow-lg w-full"
    />
  </div>
)}

<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
  <VisualCard
    id="hero-image"
    title="Hero Image"
    content={data.content_package.hero_image_prompt}
  />

  <VisualCard
    id="editorial-image"
    title="Editorial Image"
    content={data.content_package.editorial_image_prompt}

  />

  <VisualCard
    id="instagram-visual"
    title="Instagram Visual"
    content={data.content_package.instagram_visual_prompt}

  />

  <VisualCard
    id="infographic-visual"
    title="Infographic Visual"
    content={data.content_package.infographic_visual_prompt}

  />
</div>
<div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

  <ContentCard
    
    id="visual-editorial-cover"
    title="📰 Editorial Cover"
    content={data.content_package.visual_mode_1}
    copyText={copyText}
  />

  <ContentCard
    
    id="visual-quote-card"
    title="❝ Quote Card"
    content={data.content_package.visual_mode_2}
    copyText={copyText}

  />

  <ContentCard
    
    id="visual-infographic-concept"
    title="📊 Infographic Concept"
    content={data.content_package.visual_mode_3}
    copyText={copyText}

  />

  <ContentCard
    id="visual-instagram-card"
    title="📷 Instagram Visual"
    content={data.content_package.visual_mode_4}
    copyText={copyText}

  />

</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
 
              <ContentCard
                
                id="linkedin-option-1"
                title="💼 LinkedIn Option 1"
                content={data.content_package.linkedin_option_1}
                copyText={copyText}

              />

              <ContentCard
                id="linkedin-option-2"
                title="💼 LinkedIn Option 2"
                content={data.content_package.linkedin_option_2}
                copyText={copyText}

              />

              <ContentCard
                id="x-option-1"
                title="🐦 X Option 1"
                content={data.content_package.x_option_1}
                copyText={copyText}

              />

              <ContentCard
                id="x-option-2"
                title="🐦 X Option 2"
                content={data.content_package.x_option_2}
                copyText={copyText}

              />

              <ContentCard
                
                id="instagram-option-1"
                title="📷 Instagram Option 1"
                content={data.content_package.instagram_option_1}
                copyText={copyText}
              />

              <ContentCard
                id="instagram-option-2"
                title="📷 Instagram Option 2"
                content={data.content_package.instagram_option_2}
                copyText={copyText}

                           />

            </div>
          </div>
        )}
      </div>
    </div>
  </main>
);
}

function ContentCard({
  id,
  title,
  content,
  copyText,
}: {
  id: string;
  title: string;
  content: string;
  copyText: (text: string) => void;
}) {
  return (
    <div
  id={id}
  className="bg-[#FFFDF8] rounded-[28px] border border-[#E7E1D8] p-8 shadow-sm"
>
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-bold text-lg">
          {title}
        </h3>

        <button
          onClick={() => copyText(content)}
          className="bg-[#171615] text-white px-4 py-2 rounded-xl text-sm hover:bg-[#2B2927]"
        >
          Copy
        </button>
      </div>

      <div className="text-sm whitespace-pre-wrap leading-7 text-slate-700">
        {content}
      </div>
    </div>
  );
}

function VisualCard({
  id,
  title,
  content,
}: {
  id: string;
  title: string;
  content: string;
}) {
  return (
    <div
  id={id}
  className="rounded-[32px] bg-[#FFFDF8] border border-[#E7E1D8] p-6 shadow-sm"
>
      <div className="h-40 rounded-[24px] bg-gradient-to-br from-[#F5EFE3] via-[#E9E4D9] to-[#DDE7DD] mb-5"></div>

      <p className="text-xs uppercase tracking-[3px] text-[#8B8175] mb-2">
        {title}
      </p>

      <p className="text-sm leading-6 text-[#5F574F]">
        {content}
      </p>
    </div>
  );
}
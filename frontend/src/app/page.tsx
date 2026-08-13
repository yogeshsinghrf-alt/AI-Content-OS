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
import VisualStudio from "../components/VisualStudio";
import CarouselDeck from "../components/CarouselDeck";
import SocialContentTabs from "../components/SocialContentTabs";
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
  const [linkedinImage, setLinkedinImage] = useState("");
  const [instagramImage, setInstagramImage] = useState("");
  const [xImage, setXImage] = useState("");
  const [carouselImage, setCarouselImage] = useState("");
  const [infographicImage, setInfographicImage] = useState("");
  const [quoteImage, setQuoteImage] = useState("");
  const [historySearch, setHistorySearch] = useState("");
  const [generationError, setGenerationError] =
    useState<string | null>(null);
  const [historyTopic, setHistoryTopic] = useState("all");
  useEffect(() => {
  fetchHistory();
}, []);
  
async function fetchHistory() {
  try {
    const response = await fetch(
      `${API}/history/`
    );

    if (!response.ok) {
      throw new Error(
        `History request failed: ${response.status}`
      );
    }

    const result =
      await response.json();

    setHistory(result);

  } catch (error) {
    console.error(
      "Could not load history:",
      error
    );

    setHistory([]);
  }
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
  setGenerationError(null);
  
  setLoading(true);

  try {
    const response = await fetch(
  `${API}/package/daily?topic=${topic}`
);

const result = await response.json();

if (!response.ok) {
  const detail = result?.detail;

  if (
    detail?.code ===
    "AI_QUOTA_UNAVAILABLE"
  ) {
    setGenerationError(
      "AI generation is temporarily unavailable because the provider quota has been reached. Your existing content and history are still available."
    );

    return;
  }

  if (
    detail?.code ===
    "AI_SERVICE_UNAVAILABLE"
  ) {
    setGenerationError(
      "The AI content service is temporarily unavailable. Please try again later."
    );

    return;
  }

  setGenerationError(
    detail?.message ||
      "Content generation failed. Please try again."
  );

  return;
}
    if (!response.ok) {
  const detail = result?.detail;

  if (detail?.code === "AI_QUOTA_UNAVAILABLE") {
    setGenerationError(
      "AI generation is temporarily unavailable because the provider quota has been reached. Your existing content and history are still available."
    );

    setLoading(false);
    return;
  }

  if (detail?.code === "AI_SERVICE_UNAVAILABLE") {
    setGenerationError(
      "The AI content service is temporarily unavailable. Please try again later."
    );

    setLoading(false);
    return;
  }

  setGenerationError(
    detail?.message ||
      "Content generation failed. Please try again."
  );

  setLoading(false);
  return;
}

    if (
      typeof result.content_package === "string"
    ) {
      try {
        result.content_package = JSON.parse(
          result.content_package
        );
      } catch {
        throw new Error(
          "Generated content could not be parsed."
        );
      }
    }

    setData(result);
    console.log(
      "Generated package ID:",
      result.package_id
    );

    // Reset previous visuals
setHeroImage("");
setLinkedinImage("");
setInstagramImage("");
setXImage("");
setCarouselImage("");
setInfographicImage("");
setQuoteImage("");


// ------------------------------------
// Generate platform visuals in parallel
// ------------------------------------

try {
  const content = result.content_package || {};

  const linkedinPrompt =
    content.editorial_image_prompt ||
    content.hero_image_prompt ||
    result.article_title ||
    "Premium business editorial visual";

  const instagramPrompt =
    content.instagram_visual_prompt ||
    content.hero_image_prompt ||
    result.article_title ||
    "Premium Instagram editorial visual";

  const xPrompt =
    content.hero_image_prompt ||
    content.editorial_image_prompt ||
    result.article_title ||
    "Premium wide business editorial visual";

  async function generatePlatformImage(
  prompt: string,
  platform: string
) {
  const params = new URLSearchParams({
    prompt,
    platform,
  });

  if (result.package_id) {
    params.set(
      "package_id",
      result.package_id
    );
  }

  const url =
    `${API}/image/generate?${params.toString()}`;

  // First attempt
  let response = await fetch(url);

  // Retry once for temporary server/image-generation failures
  if (!response.ok && response.status >= 500) {
    console.warn(
      `${platform} image failed. Retrying...`
    );

    await new Promise((resolve) =>
      setTimeout(resolve, 1500)
    );

    response = await fetch(url);
  }

  if (!response.ok) {
    let detail = "";

    try {
      const errorData = await response.json();

      detail =
        errorData?.detail ||
        errorData?.message ||
        "";
    } catch {
      // Keep generic error below
    }

    throw new Error(
      `${platform} image failed: ${response.status}${
        detail ? ` - ${detail}` : ""
      }`
    );
  }

  return response.json();
}

  const [
    linkedinResult,
    instagramResult,
    xResult,
  ] = await Promise.allSettled([
    generatePlatformImage(
      linkedinPrompt,
      "linkedin"
    ),
    generatePlatformImage(
      instagramPrompt,
      "instagram"
    ),
    generatePlatformImage(
      xPrompt,
      "x"
    ),
  ]);

  if (
    linkedinResult.status === "fulfilled"
  ) {
    const url =
      linkedinResult.value.image_url || "";

    setLinkedinImage(url);
    setHeroImage(url);
  }

  if (
    instagramResult.status === "fulfilled"
  ) {
    setInstagramImage(
      instagramResult.value.image_url || ""
    );
  }

  if (
    xResult.status === "fulfilled"
  ) {
    setXImage(
      xResult.value.image_url || ""
    );
  }

  if (
    linkedinResult.status === "rejected"
  ) {
    console.error(
      "LinkedIn visual failed:",
      linkedinResult.reason
    );
  }

  if (
    instagramResult.status === "rejected"
  ) {
    console.error(
      "Instagram visual failed:",
      instagramResult.reason
    );
  }

  if (
    xResult.status === "rejected"
  ) {
    console.error(
      "X visual failed:",
      xResult.reason
    );
  }

} catch (imageError) {
  console.error(
    "Platform visual generation failed:",
    imageError
  );
}
  } catch (error) {
    console.error(
      "Generate Content failed:",
      error
    );

    alert(
      "Could not generate the content package. Please make sure the backend is running."
    );

  } finally {
    setLoading(false);
  }
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
   <div className="space-y-0">
  <Header />
  <div className="mt-7">
   <Toolbar
     topic={topic}
     loading={loading}
     onTopicChange={setTopic}
     onGenerate={generateContent}
     onCopyAll={copyAllContent}
     onExportPDF={() => window.print()}
   />
   {generationError && (
  <div className="mt-5 rounded-[24px] border border-[#E4D6C4] bg-[#FFF9EF] px-6 py-5">
    <div className="flex items-start gap-4">

      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#F2E6D5] font-bold text-[#8A6749]">
        !
      </div>

      <div>
        <p className="text-xs font-bold uppercase tracking-[3px] text-[#9A7654]">
          AI Service Notice
        </p>

        <h3
          className="mt-1 text-xl text-[#171615]"
          style={{
            fontFamily: "Instrument Serif",
          }}
        >
          Content generation temporarily unavailable
        </h3>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-[#6F675E]">
          {generationError}
        </p>

        <button
          type="button"
          onClick={() =>
            setGenerationError(null)
          }
          className="mt-3 text-xs font-semibold uppercase tracking-[2px] text-[#171615]"
        >
          Dismiss
        </button>
      </div>

    </div>
  </div>
)}
  </div>
  </div>
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
<VisualStudio
  headline={
    data.content_package.editorial_headline ||
    data.article_title ||
    "AI Intelligence Brief"
  }

  linkedinText={
    data.content_package.linkedin_option_1 || ""
  }

  instagramText={
    data.content_package.instagram_option_1 || ""
  }

  xText={
    data.content_package.x_option_1 || ""
  }

  carouselText={
    data.content_package.visual_mode_1 ||
    data.content_package.editorial_subtitle ||
    ""
  }

  infographicText={
    Array.isArray(
      data.content_package.infographic_points
    )
      ? data.content_package.infographic_points.join(
          " • "
        )
      : data.content_package.visual_mode_3 || ""
  }
   infographicPoints={
  Array.isArray(
    data.content_package.infographic_points
  )
    ? data.content_package.infographic_points
    : []
  }
  quoteText={
    data.content_package.quote_card ||
    data.content_package.visual_mode_2 ||
    ""
  }

  linkedinImage={
    linkedinImage || heroImage || undefined
  }

  instagramImage={
    instagramImage || heroImage || undefined
  }

  xImage={
    xImage || heroImage || undefined
  }

  carouselImage={
  carouselImage ||
  linkedinImage ||
  heroImage ||
  undefined
}

infographicImage={
  infographicImage ||
  instagramImage ||
  heroImage ||
  undefined
}

quoteImage={
  quoteImage ||
  xImage ||
  heroImage ||
  undefined
}
  source={data.source}
  packageId={data.package_id}
/>
<CarouselDeck
  headline={
    data.content_package.editorial_headline ||
    data.article_title ||
    "Industry Intelligence"
  }
  subtitle={
    data.content_package.editorial_subtitle || ""
  }
  points={
    Array.isArray(
      data.content_package.infographic_points
    )
      ? data.content_package.infographic_points
      : []
  }

  source={data.source}
  imageUrl={
    carouselImage ||
    heroImage ||
    undefined
  }
  packageId={data.package_id}
/>

<div className="mt-10 mb-8">
  <p className="text-xs uppercase tracking-[4px] text-[#8B8175] mb-3">
    VISUAL DIRECTIONS
  </p>

  <h2 className="text-4xl font-black text-[#171615]">
    Image & Infographic Concepts
  </h2>
</div>


<div className="grid grid-cols-1 md:grid-cols-2 gap-6"> 
              <SocialContentTabs
  linkedin1={
    data.content_package.linkedin_option_1
  }
  linkedin2={
    data.content_package.linkedin_option_2
  }
  x1={
    data.content_package.x_option_1
  }
  x2={
    data.content_package.x_option_2
  }
  instagram1={
    data.content_package.instagram_option_1
  }
  instagram2={
    data.content_package.instagram_option_2
  }
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
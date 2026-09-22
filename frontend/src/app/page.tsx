"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import { toPng } from "html-to-image";
import Sidebar from "../components/Sidebar";
import HistoryPanel from "../components/HistoryPanel";
import DashboardStats from "../components/DashboardStats";
import Header from "../components/Header";
import Toolbar from "../components/Toolbar";
import SourcePanel from "../components/SourcePanel";
import VisualStudio from "../components/VisualStudio";
import CarouselDeck from "../components/CarouselDeck";
import SocialContentTabs from "../components/SocialContentTabs";
import SystemStatus from "../components/SystemStatus";
import BrandProfilePanel, {
  type BrandProfile,
} from "../components/BrandProfilePanel";

type SourceMode =
  | "industry"
  | "company";

const API = "/api/backend";


type Story = {
  slot: string;
  source: string;
  title: string;
  link: string;
};
const DEFAULT_BRAND_PROFILE: BrandProfile = {
  enabled: false,
  companyName: "",
  audience: "",
  tone: "",
  cta: "",
  primaryColor: "#A67C52",
  secondaryColor: "#F7F3EB",
};
export default function Home() {
  const packageRef =
    useRef<HTMLDivElement | null>(null);  
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState("ai");
  const [sourceMode, setSourceMode] =
  useState<SourceMode>(
    "industry"
  );

  const [
  companyArticleUrl,
  setCompanyArticleUrl,
  ] = useState("");  
  const [history, setHistory] = useState<any[]>([]);
  const [activeView, setActiveView] = useState("dashboard");
  const [historySearch, setHistorySearch] = useState("");
  const [historyTopic, setHistoryTopic] = useState("all");
  const [generationError, setGenerationError] =
    useState<string | null>(null);
  const [imageGenerationNotice, setImageGenerationNotice] =
    useState<string | null>(null);
  const [brandProfile, setBrandProfile] =
  useState<BrandProfile>(
    DEFAULT_BRAND_PROFILE
  );    

  const [linkedinImage1, setLinkedinImage1] = useState("");
  const [linkedinImage2, setLinkedinImage2] = useState("");
  const [instagramImage1, setInstagramImage1] = useState("");
  const [instagramImage2, setInstagramImage2] = useState("");
  const [xImage1, setXImage1] = useState("");
  const [xImage2, setXImage2] = useState("");

useEffect(() => {
  fetchHistory();

  try {
    const saved =
      localStorage.getItem(
        "ai-content-os-brand-profile-v1"
      );

    if (saved) {
      setBrandProfile(
        JSON.parse(saved)
      );
    }
  } catch (error) {
    console.error(
      "Could not load Brand Profile:",
      error
    );
  }
}, []);

  async function fetchHistory() {
    try {
      const response = await fetch(`${API}/history/`);

      if (!response.ok) {
        throw new Error(
          `History request failed: ${response.status}`
        );
      }

      const result = await response.json();
      setHistory(result);
    } catch (error) {
      console.error("Could not load history:", error);
      setHistory([]);
    }
  }
  function getSavedAssetUrl(
  result: any,
  assetKey: string
) {
  const asset =
    result?.assets?.[assetKey];

  const filename =
    asset?.filename;

  const packageId =
    result?.package_id;

  if (!filename || !packageId) {
    return "";
  }

  const params =
    new URLSearchParams({
      package_id: packageId,
      filename,
    });

  return (
    `${API}/image/asset?` +
    params.toString()
  );
}

function restoreImages(
  result: any
) {
  setLinkedinImage1(
    getSavedAssetUrl(
      result,
      "linkedin_1"
    )
  );

  setLinkedinImage2(
    getSavedAssetUrl(
      result,
      "linkedin_2"
    )
  );

  setInstagramImage1(
    getSavedAssetUrl(
      result,
      "instagram_1"
    )
  );

  setInstagramImage2(
    getSavedAssetUrl(
      result,
      "instagram_2"
    )
  );

  setXImage1(
    getSavedAssetUrl(
      result,
      "x_1"
    )
  );

  setXImage2(
    getSavedAssetUrl(
      result,
      "x_2"
    )
  );
}
  async function loadHistory(filename: string) {
    const response = await fetch(
      `${API}/history/${filename}`
    );

    const result = await response.json();

    if (typeof result.content_package === "string") {
      try {
        result.content_package = JSON.parse(
          result.content_package
        );
      } catch {
        alert("Could not parse saved content.");
      }
    }

    setData(result);
    restoreImages(result);
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

  function resetImages() {
    setLinkedinImage1("");
    setLinkedinImage2("");
    setInstagramImage1("");
    setInstagramImage2("");
    setXImage1("");
    setXImage2("");
  }

  async function generatePlatformImage(
    prompt: string,
    platform: "linkedin" | "instagram" | "x",
    packageId?: string,
    slot?: string
  ) {
    const params = new URLSearchParams({
      prompt,
      platform,
    });

    if (packageId) {
      params.set("package_id", packageId);
    }
    if (slot) {
      params.set("slot", slot);
    }

    const url =
      `${API}/image/generate?${params.toString()}`;

    const response = await fetch(url);

    if (!response.ok) {
      let detail = "";

      try {
        const errorData = await response.json();
        detail =
          errorData?.detail ||
          errorData?.message ||
          "";
      } catch {
        // Keep generic error.
      }

      throw new Error(
        `${platform} image failed: ${response.status}${
          detail ? ` - ${detail}` : ""
        }`
      );
    }

    return response.json();
  }
function saveBrandProfile() {
  localStorage.setItem(
    "ai-content-os-brand-profile-v1",
    JSON.stringify(brandProfile)
  );

  alert("Brand Profile saved.");
}

function clearBrandProfile() {
  setBrandProfile(
    DEFAULT_BRAND_PROFILE
  );

  localStorage.removeItem(
    "ai-content-os-brand-profile-v1"
  );
}
  async function generateContent() {
    setGenerationError(null);
    setImageGenerationNotice(null);
    setLoading(true);

    try {
let response: Response;

if (sourceMode === "company") {
  const cleanUrl =
    companyArticleUrl.trim();

  if (!cleanUrl) {
    setGenerationError(
      "Please enter a public company-news or announcement URL."
    );
    return;
  }

  response = await fetch(
    `${API}/package/company-news`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        article_url: cleanUrl,

        brand_enabled:
          brandProfile.enabled,

        brand_name:
          brandProfile.companyName,

        brand_audience:
          brandProfile.audience,

        brand_tone:
          brandProfile.tone,

        brand_cta:
          brandProfile.cta,

        brand_primary_color:
          brandProfile.primaryColor,

        brand_secondary_color:
          brandProfile.secondaryColor,
      }),
    }
  );
} else {
  const params =
    new URLSearchParams({
      topic,
    });

  if (brandProfile.enabled) {
    params.set(
      "brand_enabled",
      "true"
    );

    params.set(
      "brand_name",
      brandProfile.companyName
    );

    params.set(
      "brand_audience",
      brandProfile.audience
    );

    params.set(
      "brand_tone",
      brandProfile.tone
    );

    params.set(
      "brand_cta",
      brandProfile.cta
    );

    params.set(
      "brand_primary_color",
      brandProfile.primaryColor
    );

    params.set(
      "brand_secondary_color",
      brandProfile.secondaryColor
    );
  }

  response = await fetch(
    `${API}/package/daily?${params.toString()}`
  );
}

      const result = await response.json();

      if (!response.ok) {
        const detail = result?.detail;
if (
  detail?.code ===
  "INVALID_COMPANY_NEWS_URL"
) {
  setGenerationError(
    "Please enter a valid public company-news or announcement URL."
  );
  return;
}

if (
  detail?.code ===
  "COMPANY_NEWS_FETCH_FAILED"
) {
  setGenerationError(
    "The company article could not be read. Please check that the page is public and try another URL."
  );
  return;
}        

        if (
          detail?.code === "AI_QUOTA_UNAVAILABLE"
        ) {
          setGenerationError(
            "AI generation is temporarily unavailable because the provider quota has been reached. Your existing content and history are still available."
          );
          return;
        }

        if (
          detail?.code === "AI_SERVICE_UNAVAILABLE"
        ) {
          setGenerationError(
            "The AI content service is temporarily unavailable. Please try again later."
          );
          return;
        }
      if (
  detail?.code === "INSUFFICIENT_DISTINCT_STORIES"
) {
  const available =
    detail?.available ?? 0;

  const required =
    detail?.required ?? 8;

  setGenerationError(
    `Only ${available} distinct current stories are available right now, but ${required} are required to build a complete package. Please try again later or choose another topic.`
  );

  return;
}  

        setGenerationError(
          detail?.message ||
            "Content generation failed. Please try again."
        );
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
      resetImages();

      const content = result.content_package || {};

      const imageJobs = [
        {
          key: "linkedin1",
          slot: "linkedin_1",
          platform: "linkedin" as const,
          prompt:
            content.linkedin_1_visual_prompt ||
            content.editorial_image_prompt ||
            result.article_title ||
            "Premium business editorial visual",
        },
        {
          key: "linkedin2",
          slot: "linkedin_2",
          platform: "linkedin" as const,
          prompt:
            content.linkedin_2_visual_prompt ||
            content.editorial_image_prompt ||
            result.article_title ||
            "Premium business editorial visual",
        },
        {
          key: "instagram1",
          slot: "instagram_1",
          platform: "instagram" as const,
          prompt:
            content.instagram_1_visual_prompt ||
            content.instagram_visual_prompt ||
            result.article_title ||
            "Premium Instagram editorial visual",
        },
        {
          key: "instagram2",
          slot: "instagram_2",
          platform: "instagram" as const,
          prompt:
            content.instagram_2_visual_prompt ||
            content.instagram_visual_prompt ||
            result.article_title ||
            "Premium Instagram editorial visual",
        },
        {
          key: "x1",
          slot: "x_1",
          platform: "x" as const,
          prompt:
            content.x_1_visual_prompt ||
            content.hero_image_prompt ||
            result.article_title ||
            "Premium wide editorial visual",
        },
        {
          key: "x2",
          slot: "x_2",
          platform: "x" as const,
          prompt:
            content.x_2_visual_prompt ||
            content.hero_image_prompt ||
            result.article_title ||
            "Premium wide editorial visual",
        },
      ];

      const settled = await Promise.allSettled(
        imageJobs.map((job) =>
          generatePlatformImage(
            job.prompt,
            job.platform,
            result.package_id,
            job.slot
          )
        )
      );

let failedImageCount = 0;
let fallbackImageCount = 0;

settled.forEach((item, index) => {
  const key = imageJobs[index].key;

  if (item.status === "rejected") {
    failedImageCount += 1;

    console.error(
      `${key} image failed:`,
      item.reason
    );

    return;
  }

  const url =
    item.value.image_url || "";

  if (item.value.fallback_used) {
    fallbackImageCount += 1;
  }

  if (key === "linkedin1") {
    setLinkedinImage1(url);
  }

  if (key === "linkedin2") {
    setLinkedinImage2(url);
  }

  if (key === "instagram1") {
    setInstagramImage1(url);
  }

  if (key === "instagram2") {
    setInstagramImage2(url);
  }

  if (key === "x1") {
    setXImage1(url);
  }

  if (key === "x2") {
    setXImage2(url);
  }
});

if (
  failedImageCount > 0 ||
  fallbackImageCount > 0
) {
  const parts: string[] = [];

  if (failedImageCount > 0) {
    parts.push(
      `${failedImageCount} visual${
        failedImageCount === 1 ? "" : "s"
      } could not be generated`
    );
  }

  if (fallbackImageCount > 0) {
    parts.push(
      `${fallbackImageCount} visual${
        fallbackImageCount === 1 ? "" : "s"
      } are using fallback previews`
    );
  }

  setImageGenerationNotice(
    `${parts.join(
      " and "
    )}. The written content is still available. You can try generating a fresh package later.`
  );
}

      fetchHistory();
    } catch (error) {
      console.error(
        "Generate Content failed:",
        error
      );

      setGenerationError(
        "Could not generate the content package. Please make sure the backend is available."
      );
    } finally {
      setLoading(false);
    }
  }

  function copyAllContent() {
    if (!data) return;

    navigator.clipboard.writeText(
      JSON.stringify(
        data.content_package,
        null,
        2
      )
    );

    alert("All content copied.");
  }
  async function exportPackagePng() {
    if (!packageRef.current) {
      alert(
        "Generate a content package before exporting PNG."
      );
      return;
    }

    try {
const dataUrl = await toPng(
  packageRef.current,
  {
    cacheBust: true,
    includeQueryParams: true,
    pixelRatio: 1.5,
    backgroundColor: "#F5F2EA",
  }
);

      const link =
        document.createElement("a");

      link.download =
        `AI-Content-OS-${topic}-package.png`;

      link.href = dataUrl;

      document.body.appendChild(
        link
      );

      link.click();

      document.body.removeChild(
        link
      );
    } catch (error) {
      console.error(
        "Package PNG export failed:",
        error
      );

      alert(
        "Could not export the content package as PNG."
      );
    }
  }
  const filteredHistory = history.filter((item) => {
    const matchesTopic =
      historyTopic === "all" ||
      item.topic === historyTopic;

    const search =
      historySearch.toLowerCase();

    const matchesSearch =
      item.title
        ?.toLowerCase()
        .includes(search) ||
      item.source
        ?.toLowerCase()
        .includes(search);

    return matchesTopic && matchesSearch;
  });

  function getStory(slot: string): Story {
    const stories = Array.isArray(data?.stories)
      ? data.stories
      : [];

    const match = stories.find(
      (story: Story) =>
        story.slot === slot
    );

    if (match) {
      return match;
    }

    return {
      slot,
      source:
        data?.source || "AI Content OS",
      title:
        data?.article_title ||
        "Industry Intelligence",
      link:
        data?.article_link || "",
    };
  }

  const content =
    data?.content_package || {};

  const linkedinStory1 =
    getStory("linkedin_1");
  const linkedinStory2 =
    getStory("linkedin_2");
  const instagramStory1 =
    getStory("instagram_1");
  const instagramStory2 =
    getStory("instagram_2");
  const xStory1 = getStory("x_1");
  const xStory2 = getStory("x_2");
  const infographicStory =
    getStory("infographic");
  const carouselStory =
    getStory("carousel");

  const assignedStories = data
    ? [
        ["LinkedIn 1", linkedinStory1],
        ["LinkedIn 2", linkedinStory2],
        ["Instagram 1", instagramStory1],
        ["Instagram 2", instagramStory2],
        ["X 1", xStory1],
        ["X 2", xStory2],
        ["Infographic", infographicStory],
        ["Carousel", carouselStory],
      ]
    : [];

  return (
    <main className="min-h-screen bg-[#F5F2EA] text-[#181716]">
      <div className="flex min-h-screen">
        <Sidebar
          activeView={activeView}
          setActiveView={setActiveView}
        />

        <div className="flex-1 p-8">
          {activeView === "history" && (
            <div className="rounded-[32px] border border-[#E7E1D8] bg-[#FFFDF8] p-8 shadow-sm">
              <p className="mb-4 text-xs uppercase tracking-[4px] text-[#8B8175]">
                HISTORY
              </p>

              <h1
                className="mb-8 text-5xl"
                style={{
                  fontFamily:
                    "Instrument Serif",
                }}
              >
                Saved Content Packages
              </h1>

              <div className="space-y-4">
                {history.map(
                  (item, index) => (
                    <div
                      key={index}
                      onClick={() =>
                        loadHistory(
                          item.filename
                        )
                      }
                      className="cursor-pointer rounded-2xl border border-[#E7E1D8] bg-white p-5 transition hover:shadow-md"
                    >
                      <p className="text-sm uppercase text-[#8B8175]">
                        {item.topic}
                      </p>

                      <h3 className="text-lg font-bold">
                        {item.title}
                      </h3>

                      <p className="text-sm text-slate-500">
                        {item.source}
                      </p>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteHistory(
                            item.filename
                          );
                        }}
                        className="mt-3 text-sm text-red-600 hover:underline"
                      >
                        🗑 Delete
                      </button>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          <Header />

          <div className="mt-7">
            <section className="mb-6 rounded-[28px] border border-[#E3DCD1] bg-[#FFFDF8] p-6 shadow-sm">
  <p className="text-xs font-bold uppercase tracking-[3px] text-[#A67C52]">
    SOURCE MODE
  </p>

  <h2 className="mt-2 text-2xl font-semibold text-[#181716]">
    Choose what AI Content OS should transform
  </h2>

  <div className="mt-5 flex flex-wrap gap-3">
    <button
      type="button"
      onClick={() =>
        setSourceMode(
          "industry"
        )
      }
       className={`rounded-full border px-5 py-2.5 text-sm font-semibold transition ${
       sourceMode === "industry"
       ? "border-[#A67C52] bg-[#A67C52] text-[#F7F3EB] shadow-sm"
       : "border-[#D8D0C5] bg-white text-[#5F574F] hover:border-[#A67C52]/60 hover:text-[#A67C52]"
      }`}
    >
      Industry Intelligence
    </button>

    <button
      type="button"
      onClick={() =>
        setSourceMode(
          "company"
        )
      }
      className={`rounded-full border px-5 py-2.5 text-sm font-semibold transition ${
      sourceMode === "company"
       ? "border-[#A67C52] bg-[#A67C52] text-[#F7F3EB] shadow-sm"
       : "border-[#D8D0C5] bg-white text-[#5F574F] hover:border-[#A67C52]/60 hover:text-[#A67C52]"
      }`}
    >
      Company Newsroom
    </button>
  </div>

  {sourceMode === "company" && (
    <div className="mt-5">
      <label className="mb-2 block text-xs font-bold uppercase tracking-[2px] text-[#817466]">
        Company article or announcement URL
      </label>

      <input
        type="url"
        value={
          companyArticleUrl
        }
        onChange={(event) =>
          setCompanyArticleUrl(
            event.target.value
          )
        }
        placeholder="https://company.com/news/announcement"
        className="w-full rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
      />

      <p className="mt-2 text-xs leading-5 text-[#81776D]">
        Use a public company newsroom, blog,
        press release or announcement page.
      </p>
    </div>
  )}
</section>
<Toolbar
  topic={topic}
  sourceMode={sourceMode}
  loading={loading}
  onTopicChange={setTopic}
  onGenerate={generateContent}
  onCopyAll={copyAllContent}
  onExportPDF={() =>
    window.print()
  }
  onExportPNG={
    exportPackagePng
  }
/>
<div className="mb-6">
<BrandProfilePanel
  value={brandProfile}
  onChange={setBrandProfile}
  onSave={saveBrandProfile}
  onClear={clearBrandProfile}
/>
</div>
            {generationError && (
              <div className="mt-5 rounded-[24px] border border-[#E4D6C4] bg-[#FFF9EF] px-6 py-5">
                <p className="text-xs font-bold uppercase tracking-[3px] text-[#9A7654]">
                  AI Service Notice
                </p>
                <p className="mt-2 text-sm leading-6 text-[#6F675E]">
                  {generationError}
                </p>
              </div>
            )}
{imageGenerationNotice && (
  <div className="mt-4 rounded-[24px] border border-[#D8D5CB] bg-[#FAF8F2] px-6 py-5">
    <p className="text-xs font-bold uppercase tracking-[3px] text-[#7B746B]">
      Creative Asset Notice
    </p>

    <p className="mt-2 text-sm leading-6 text-[#6F675E]">
      {imageGenerationNotice}
    </p>
  </div>
)}       
          </div>

          <DashboardStats
           topic={topic}
           sourceMode={
           data?.source_mode ===
           "company-news"
           ? "company"
           : sourceMode
          }
/>
          <SystemStatus />
          <HistoryPanel
            history={filteredHistory}
            onLoadHistory={loadHistory}
            onDeleteHistory={deleteHistory}
          />

          {data && (
            <div id="content-package"
                 ref={packageRef}
            >
              <SourcePanel
                sources={
                  data.available_sources || []
                }
              />

<section className="mt-8 rounded-[36px] border border-[#E7E1D8] bg-[#FFFDF8] p-8 shadow-sm">
  <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
    <div>
      <p className="text-xs font-bold uppercase tracking-[4px] text-[#927F68]">
        {data?.source_mode ===
        "company-news"
          ? "COMPANY NEWSROOM"
          : "MULTI-STORY DAILY INTELLIGENCE"}
      </p>

      <h2
        className="mt-2 text-4xl text-[#171615]"
        style={{
          fontFamily:
            "Instrument Serif",
        }}
      >
        {data?.source_mode ===
        "company-news"
          ? "One announcement, multiple communication formats"
          : "8 independently assigned stories"}
      </h2>

      <p className="mt-3 max-w-3xl text-sm leading-6 text-[#70665D]">
        {data?.source_mode ===
        "company-news"
          ? "LinkedIn, X, Instagram, infographic and carousel outputs are grounded in the same organisation-owned announcement."
          : "Each social option, infographic and carousel is grounded in its own assigned article."}
      </p>
    </div>

    <span className="w-fit rounded-full border border-[#DCD3C7] bg-white px-4 py-2 text-xs font-semibold text-[#6E655C]">
      {data?.source_mode ===
      "company-news"
        ? "COMPANY NEWS"
        : data.topic?.toUpperCase()}
    </span>
  </div>

  {data?.source_mode ===
  "company-news" ? (
    <article className="mt-7 rounded-[22px] border border-[#E6DED3] bg-white p-6">
      <p className="text-[10px] font-bold uppercase tracking-[3px] text-[#9A8167]">
        COMPANY SOURCE
      </p>

      <p className="mt-3 text-xs font-semibold uppercase text-[#81766A]">
        {data.source}
      </p>

      <h3 className="mt-2 text-lg font-bold leading-7 text-[#221F1C]">
        {data.article_title}
      </h3>

      {data.article_link && (
        <a
          href={
            data.article_link
          }
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-block text-xs font-semibold text-[#78644E] underline"
        >
          Read company source
        </a>
      )}
    </article>
  ) : (
    <div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {assignedStories.map(
        (
          [label, story]:
            any
        ) => (
          <article
            key={label}
            className="rounded-[22px] border border-[#E6DED3] bg-white p-5"
          >
            <p className="text-[10px] font-bold uppercase tracking-[3px] text-[#9A8167]">
              {label}
            </p>

            <p className="mt-3 text-xs font-semibold uppercase text-[#81766A]">
              {story.source}
            </p>

            <h3 className="mt-2 text-base font-bold leading-6 text-[#221F1C]">
              {story.title}
            </h3>

            {story.link && (
              <a
                href={
                  story.link
                }
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-block text-xs font-semibold text-[#78644E] underline"
              >
                Read source
              </a>
            )}
          </article>
        )
      )}
    </div>
  )}
</section>

              <div className="mb-8 mt-10">
                <p className="mb-3 text-xs uppercase tracking-[4px] text-[#8B8175]">
                  CONTENT OUTPUTS
                </p>
                <h2 className="text-4xl font-black text-[#171615]">
                  Editorial Content Collection
                </h2>
              </div>

              <SocialContentTabs
                sourceMode={
                  data?.source_mode ===
                  "company-news"
                  ? "company"
                  : "industry"
                }  
                linkedin1={
                  content.linkedin_option_1
                }
                linkedin2={
                  content.linkedin_option_2
                }
                x1={content.x_option_1}
                x2={content.x_option_2}
                instagram1={
                  content.instagram_option_1
                }
                instagram2={
                  content.instagram_option_2
                }
                linkedinStory1={
                  linkedinStory1
                }
                linkedinStory2={
                  linkedinStory2
                }
                instagramStory1={
                  instagramStory1
                }
                instagramStory2={
                  instagramStory2
                }
                xStory1={xStory1}
                xStory2={xStory2}
              />

              <VisualStudio
                sourceMode={
                   data?.source_mode ===
                  "company-news"
                    ? "company"
                    : "industry"
               }
                linkedin1={{
                  headline:
                    content.linkedin_1_headline ||
                    linkedinStory1.title,
                  content:
                    content.linkedin_option_1 ||
                    "",
                  image:
                    linkedinImage1 ||
                    undefined,
                  source:
                    linkedinStory1.source,
                }}
                linkedin2={{
                  headline:
                    content.linkedin_2_headline ||
                    linkedinStory2.title,
                  content:
                    content.linkedin_option_2 ||
                    "",
                  image:
                    linkedinImage2 ||
                    undefined,
                  source:
                    linkedinStory2.source,
                }}
                instagram1={{
                  headline:
                    content.instagram_1_headline ||
                    instagramStory1.title,
                  content:
                    content.instagram_option_1 ||
                    "",
                  image:
                    instagramImage1 ||
                    undefined,
                  source:
                    instagramStory1.source,
                }}
                instagram2={{
                  headline:
                    content.instagram_2_headline ||
                    instagramStory2.title,
                  content:
                    content.instagram_option_2 ||
                    "",
                  image:
                    instagramImage2 ||
                    undefined,
                  source:
                    instagramStory2.source,
                }}
                x1={{
                  headline:
                    content.x_1_headline ||
                    xStory1.title,
                  content:
                    content.x_option_1 ||
                    "",
                  image:
                    xImage1 ||
                    undefined,
                  source:
                    xStory1.source,
                }}
                x2={{
                  headline:
                    content.x_2_headline ||
                    xStory2.title,
                  content:
                    content.x_option_2 ||
                    "",
                  image:
                    xImage2 ||
                    undefined,
                  source:
                    xStory2.source,
                }}
                infographic={{
                  headline:
                    content.infographic_headline ||
                    infographicStory.title,
                  subtitle:
                    content.editorial_subtitle ||
                    "",
                  points: Array.isArray(
                    content.infographic_points
                  )
                    ? content.infographic_points
                    : [],
                  source:
                    infographicStory.source,
                }}
                carousel={{
                  headline:
                    content.carousel_headline ||
                    carouselStory.title,
                  source:
                    carouselStory.source,
                }}
                packageId={
                  data.package_id
                }
                brandEnabled={
  Boolean(
    data?.brand_profile?.enabled
  )
}
brandName={
  data?.brand_profile?.company_name ||
  ""
}
primaryColor={
  data?.brand_profile?.primary_color ||
  ""
}
secondaryColor={
  data?.brand_profile?.secondary_color ||
  ""
}
              />

              <div className="mt-10">
<CarouselDeck
  headline={
    content.carousel_headline ||
    carouselStory.title ||
    "Industry Intelligence"
  }
  subtitle=""
  slides={
    Array.isArray(
      content.carousel_slides
    )
      ? content.carousel_slides
      : []
  }
  source={
    carouselStory.source
  }
  packageId={
    data.package_id
  }
  brandEnabled={
    data.brand_profile?.enabled
  }
  brandName={
    data.brand_profile?.company_name
  }
  primaryColor={
    data.brand_profile?.primary_color
  }
  secondaryColor={
    data.brand_profile?.secondary_color
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

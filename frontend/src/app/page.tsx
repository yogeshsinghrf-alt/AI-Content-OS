"use client";

import { useEffect, useState } from "react";
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

type Story = {
  slot: string;
  source: string;
  title: string;
  link: string;
};

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState("ai");
  const [history, setHistory] = useState<any[]>([]);
  const [activeView, setActiveView] = useState("dashboard");
  const [historySearch, setHistorySearch] = useState("");
  const [historyTopic, setHistoryTopic] = useState("all");
  const [generationError, setGenerationError] =
    useState<string | null>(null);

  const [linkedinImage1, setLinkedinImage1] = useState("");
  const [linkedinImage2, setLinkedinImage2] = useState("");
  const [instagramImage1, setInstagramImage1] = useState("");
  const [instagramImage2, setInstagramImage2] = useState("");
  const [xImage1, setXImage1] = useState("");
  const [xImage2, setXImage2] = useState("");

  useEffect(() => {
    fetchHistory();
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
    resetImages();
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
    packageId?: string
  ) {
    const params = new URLSearchParams({
      prompt,
      platform,
    });

    if (packageId) {
      params.set("package_id", packageId);
    }

    const url =
      `${API}/image/generate?${params.toString()}`;

    let response = await fetch(url);

    if (!response.ok && response.status >= 500) {
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
          platform: "linkedin" as const,
          prompt:
            content.linkedin_1_visual_prompt ||
            content.editorial_image_prompt ||
            result.article_title ||
            "Premium business editorial visual",
        },
        {
          key: "linkedin2",
          platform: "linkedin" as const,
          prompt:
            content.linkedin_2_visual_prompt ||
            content.editorial_image_prompt ||
            result.article_title ||
            "Premium business editorial visual",
        },
        {
          key: "instagram1",
          platform: "instagram" as const,
          prompt:
            content.instagram_1_visual_prompt ||
            content.instagram_visual_prompt ||
            result.article_title ||
            "Premium Instagram editorial visual",
        },
        {
          key: "instagram2",
          platform: "instagram" as const,
          prompt:
            content.instagram_2_visual_prompt ||
            content.instagram_visual_prompt ||
            result.article_title ||
            "Premium Instagram editorial visual",
        },
        {
          key: "x1",
          platform: "x" as const,
          prompt:
            content.x_1_visual_prompt ||
            content.hero_image_prompt ||
            result.article_title ||
            "Premium wide editorial visual",
        },
        {
          key: "x2",
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
            result.package_id
          )
        )
      );

      settled.forEach((item, index) => {
        const key = imageJobs[index].key;

        if (item.status === "rejected") {
          console.error(
            `${key} image failed:`,
            item.reason
          );
          return;
        }

        const url =
          item.value.image_url || "";

        if (key === "linkedin1") setLinkedinImage1(url);
        if (key === "linkedin2") setLinkedinImage2(url);
        if (key === "instagram1") setInstagramImage1(url);
        if (key === "instagram2") setInstagramImage2(url);
        if (key === "x1") setXImage1(url);
        if (key === "x2") setXImage2(url);
      });

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
            <Toolbar
              topic={topic}
              loading={loading}
              onTopicChange={setTopic}
              onGenerate={generateContent}
              onCopyAll={copyAllContent}
              onExportPDF={() =>
                window.print()
              }
            />

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
          </div>

          <DashboardStats topic={topic} />

          <HistoryPanel
            history={filteredHistory}
            onLoadHistory={loadHistory}
            onDeleteHistory={deleteHistory}
          />

          {data && (
            <div id="content-package">
              <SourcePanel
                sources={
                  data.available_sources || []
                }
              />

              <section className="mt-8 rounded-[36px] border border-[#E7E1D8] bg-[#FFFDF8] p-8 shadow-sm">
                <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[4px] text-[#927F68]">
                      MULTI-STORY DAILY INTELLIGENCE
                    </p>
                    <h2
                      className="mt-2 text-4xl text-[#171615]"
                      style={{
                        fontFamily:
                          "Instrument Serif",
                      }}
                    >
                      8 independently assigned stories
                    </h2>
                    <p className="mt-3 max-w-3xl text-sm leading-6 text-[#70665D]">
                      Each social option, infographic and carousel is grounded in its own assigned article.
                    </p>
                  </div>

                  <span className="w-fit rounded-full border border-[#DCD3C7] bg-white px-4 py-2 text-xs font-semibold text-[#6E655C]">
                    {data.topic?.toUpperCase()}
                  </span>
                </div>

                <div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {assignedStories.map(
                    ([label, story]: any) => (
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
                            href={story.link}
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
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

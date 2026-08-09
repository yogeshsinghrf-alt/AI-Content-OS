"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

type Platform =
  | "linkedin"
  | "instagram"
  | "x"
  | "carousel"
  | "infographic"
  | "quote";

type VisualPostCardProps = {
  platform: Platform;
  headline: string;
  content: string;
  imageUrl?: string;
  source?: string;
};

const platformConfig = {
  linkedin: {
    width: 1200,
    height: 1200,
    label: "LINKEDIN",
    previewScale: 0.34,
  },
  instagram: {
    width: 1080,
    height: 1350,
    label: "INSTAGRAM",
    previewScale: 0.55,
  },
  x: {
    width: 1600,
    height: 900,
    label: "X",
    previewScale: 0.28,
  },
  carousel: {
    width: 1080,
    height: 1080,
    label: "CAROUSEL",
    previewScale: 0.34,
  },
  infographic: {
    width: 1080,
    height: 1350,
    label: "INFOGRAPHIC",
    previewScale: 0.3,
  },
  quote: {
    width: 1080,
    height: 1080,
    label: "QUOTE",
    previewScale: 0.34,
  },
};

function shortenText(text: string, limit: number) {
  if (!text) return "";

  return text.length > limit
    ? `${text.slice(0, limit).trim()}…`
    : text;
}
function cleanDisplayText(
  text: string,
  limit: number
) {
  if (!text) return "";

  const cleaned = text
    // Remove URLs
    .replace(/https?:\/\/\S+/g, "")
    // Remove hashtags from visual artwork
    .replace(/#[\w-]+/g, "")
    // Remove excessive whitespace
    .replace(/\s+/g, " ")
    .trim();

  return shortenText(cleaned, limit);
}
export default function VisualPostCard({
  platform,
  headline,
  content,
  imageUrl,
  source,
}: VisualPostCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const config = platformConfig[platform];
  async function createPng() {
  if (!cardRef.current) {
    throw new Error("Visual card not found.");
  }

  return await toPng(cardRef.current, {
    cacheBust: true,
    pixelRatio: 1,
    width: config.width,
    height: config.height,
  });
}

async function downloadPng() {
  try {
    const dataUrl = await createPng();

    const link = document.createElement("a");
    link.download = `${platform}-post.png`;
    link.href = dataUrl;
    link.click();
  } catch (error) {
    console.error("PNG export error:", error);
    alert("PNG export failed.");
  }
}

async function downloadPdf() {
  try {
    const dataUrl = await createPng();

    const orientation =
      config.width > config.height
        ? "landscape"
        : "portrait";

    const pdf = new jsPDF({
      orientation,
      unit: "px",
      format: [config.width, config.height],
    });

    pdf.addImage(
      dataUrl,
      "PNG",
      0,
      0,
      config.width,
      config.height
    );

    pdf.save(`${platform}-post.pdf`);
  } catch (error) {
    console.error("PDF export error:", error);
    alert("PDF export failed.");
  }
}

async function printCard() {
  try {
    const dataUrl = await createPng();

    const printWindow = window.open("", "_blank");

    if (!printWindow) {
      alert("Please allow pop-ups for printing.");
      return;
    }

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>${config.label}</title>
          <style>
            html, body {
              margin: 0;
              padding: 0;
              background: white;
            }

            body {
              min-height: 100vh;
              display: flex;
              justify-content: center;
              align-items: center;
            }

            img {
              display: block;
              max-width: 100%;
              max-height: 100vh;
              object-fit: contain;
            }

            @page {
              margin: 0;
            }
          </style>
        </head>

        <body>
          <img src="${dataUrl}" />

          <script>
            window.onload = function () {
              window.focus();
              window.print();
            };
          </script>
        </body>
      </html>
    `);

    printWindow.document.close();
  } catch (error) {
    console.error("Print error:", error);
    alert("Print preparation failed.");
  }
}
  const backgroundStyle = imageUrl
    ? {
        backgroundImage: `url("${imageUrl}")`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }
    : {
        background:
          "linear-gradient(145deg, #EEE6D8 0%, #DDE6DF 50%, #BCCFC5 100%)",
      };

  function renderLinkedIn() {
    return (
      <div className="relative flex h-full flex-col overflow-hidden bg-[#F6F0E6] text-[#171615]">
        <div className="h-[54%] overflow-hidden">
          <div
            className="h-full w-full"
            style={backgroundStyle}
          />
        </div>

        <div className="flex flex-1 flex-col justify-between p-14">
          <div>
            <p className="mb-6 text-xl font-semibold uppercase tracking-[0.28em] text-[#84796B]">
              EXECUTIVE BRIEF
            </p>

            <h2
              className="max-w-[92%] text-6xl leading-[0.98]"
              style={{ fontFamily: "Instrument Serif" }}
            >
              {shortenText(headline, 105)}
            </h2>

            <p className="mt-7 max-w-[90%] text-2xl leading-relaxed text-[#5E574F]">
              {cleanDisplayText(content, 150)}
            </p>
          </div>

          <div className="flex items-center justify-between border-t border-[#D9D0C3] pt-6 text-lg">
            <strong>AI CONTENT OS</strong>
            <span>{source || "Industry Intelligence"}</span>
          </div>
        </div>
      </div>
    );
  }

  function renderInstagram() {
    return (
      <div
        className="relative h-full overflow-hidden text-white"
        style={backgroundStyle}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-black/20 to-black/90" />

        <div className="relative flex h-full flex-col justify-between p-14">
          <div className="flex items-center justify-between">
            <p className="text-xl font-bold tracking-[0.3em]">
              AI CONTENT OS
            </p>

            <div className="rounded-full border border-white/40 bg-white/10 px-6 py-3 text-lg backdrop-blur-lg">
              EDITORIAL
            </div>
          </div>

          <div>
            <p className="mb-7 text-xl uppercase tracking-[0.3em] text-white/70">
              THE BRIEF
            </p>

            <h2
              className="text-7xl leading-[0.95]"
              style={{ fontFamily: "Instrument Serif" }}
            >
              {shortenText(headline, 72)}
            </h2>

            <p className="mt-8 max-w-[90%] text-2xl leading-relaxed text-white/85">
              {cleanDisplayText(content, 105)}
            </p>
          </div>

          <div className="border-t border-white/30 pt-6 text-lg text-white/75">
            {source || "AI • Telecom • Marketing"}
          </div>
        </div>
      </div>
    );
  }

  function renderX() {
    return (
      <div className="flex h-full bg-[#111312] text-white">
        <div
          className="w-[54%] bg-cover bg-center"
          style={backgroundStyle}
        />

        <div className="flex w-[46%] flex-col justify-between p-14">
          <div className="flex items-center justify-between">
            <strong className="text-xl tracking-[0.24em]">
              AI CONTENT OS
            </strong>

            <span className="rounded-full border border-white/20 px-5 py-2 text-lg">
              X
            </span>
          </div>

          <div>
            <p className="mb-6 text-lg uppercase tracking-[0.28em] text-white/50">
              SIGNAL / TODAY
            </p>

            <h2
              className="text-6xl leading-[0.98]"
              style={{ fontFamily: "Instrument Serif" }}
            >
              {shortenText(headline, 68)}
            </h2>

            <p className="mt-7 text-2xl leading-relaxed text-white/70">
              {cleanDisplayText(content, 95)}
            </p>
          </div>

          <p className="border-t border-white/20 pt-6 text-lg text-white/50">
            {source || "Industry Intelligence"}
          </p>
        </div>
      </div>
    );
  }

  function renderCarousel() {
    return (
      <div className="relative h-full overflow-hidden bg-[#F4EFE6] text-[#171615]">
        <div
          className="absolute right-0 top-0 h-full w-[48%]"
          style={backgroundStyle}
        />

        <div className="absolute right-[42%] top-0 h-full w-40 bg-gradient-to-r from-[#F4EFE6] to-transparent" />

        <div className="relative flex h-full w-[64%] flex-col justify-between p-14">
          <div>
            <p className="text-xl font-bold tracking-[0.28em] text-[#776D61]">
              AI CONTENT OS
            </p>

            <p className="mt-16 text-xl uppercase tracking-[0.3em] text-[#9A8E7F]">
              Carousel • Slide 01
            </p>

            <h2
              className="mt-7 text-7xl leading-[0.94]"
              style={{ fontFamily: "Instrument Serif" }}
            >
              {shortenText(headline, 85)}
            </h2>

            <p className="mt-8 max-w-[85%] text-2xl leading-relaxed text-[#625A51]">
              {shortenText(content, 180)}
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="h-3 w-16 rounded-full bg-[#171615]" />
            <div className="h-3 w-3 rounded-full bg-[#C8BFAF]" />
            <div className="h-3 w-3 rounded-full bg-[#C8BFAF]" />
            <div className="h-3 w-3 rounded-full bg-[#C8BFAF]" />
          </div>
        </div>
      </div>
    );
  }

  function renderInfographic() {
  const points = content
    .split("•")
    .map((point) => point.trim())
    .filter(Boolean)
    .slice(0, 4);

  const safePoints =
    points.length > 0
      ? points
      : [
          "A major shift is happening in the market.",
          "Adoption is accelerating across industries.",
          "Business impact is becoming measurable.",
          "Early movers may gain a competitive advantage.",
        ];

  return (
    <div className="flex h-full flex-col bg-[#F7F3EB] p-14 text-[#171615]">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-lg font-bold tracking-[0.28em]">
            AI CONTENT OS
          </p>

          <p className="mt-2 text-sm uppercase tracking-[0.24em] text-[#8B8175]">
            Intelligence Infographic
          </p>
        </div>

        <div className="rounded-full bg-[#DFE8DF] px-6 py-3 text-lg font-semibold text-[#365243]">
          KEY SIGNALS
        </div>
      </div>

      {/* Headline */}
      <h2
        className="mt-12 max-w-[92%] text-6xl leading-[0.98]"
        style={{
          fontFamily: "Instrument Serif",
        }}
      >
        {shortenText(headline, 90)}
      </h2>

      {/* Insight cards */}
      <div className="mt-12 grid grid-cols-2 gap-7">
        {safePoints.map((point, index) => (
          <div
            key={index}
            className="rounded-[32px] border border-[#DED7CC] bg-[#FFFDF9] p-8 shadow-sm"
          >
            <div className="flex items-center justify-between">

              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#E8DFCE] text-2xl font-bold">
                {index + 1}
              </div>

              <span className="text-sm font-semibold uppercase tracking-[2px] text-[#A19383]">
                Signal
              </span>
            </div>

            <p className="mt-7 text-2xl leading-relaxed text-[#5E574F]">
              {shortenText(point, 120)}
            </p>
          </div>
        ))}
      </div>

      {/* Big takeaway */}
      <div className="mt-8 rounded-[34px] bg-[#1D211E] p-9 text-white">
        <p className="text-sm font-semibold uppercase tracking-[3px] text-white/55">
          THE TAKEAWAY
        </p>

        <p
          className="mt-5 text-3xl leading-snug"
          style={{
            fontFamily: "Instrument Serif",
          }}
        >
          This development matters most where it creates
          measurable business value, not just technological novelty.
        </p>
      </div>

      {/* Footer */}
      <div className="mt-auto flex items-center justify-between border-t border-[#D8D0C4] pt-6 text-lg text-[#766D63]">
        <span>{source || "Industry Intelligence"}</span>

        <span>
          AI • Telecom • Marketing
        </span>
      </div>

    </div>
  );
}

  function renderQuote() {
    return (
      <div
        className="relative h-full overflow-hidden text-white"
        style={backgroundStyle}
      >
        <div className="absolute inset-0 bg-[#1A201D]/80" />

        <div className="relative flex h-full flex-col justify-between p-16">
          <div className="flex items-center justify-between">
            <strong className="text-xl tracking-[0.25em]">
              AI CONTENT OS
            </strong>

            <span className="text-7xl text-[#DCC8A8]">❝</span>
          </div>

          <blockquote
            className="max-w-[92%] text-6xl leading-[1.05]"
            style={{ fontFamily: "Instrument Serif" }}
          >
            {shortenText(content, 210)}
          </blockquote>

          <div className="border-t border-white/25 pt-7 text-xl text-white/70">
            {source || "An idea worth sharing"}
          </div>
        </div>
      </div>
    );
  }

  function renderDesign() {
    switch (platform) {
      case "linkedin":
        return renderLinkedIn();
      case "instagram":
        return renderInstagram();
      case "x":
        return renderX();
      case "carousel":
        return renderCarousel();
      case "infographic":
        return renderInfographic();
      case "quote":
        return renderQuote();
      default:
        return renderLinkedIn();
    }
  }

  return (
    <div className="rounded-[32px] border border-[#E7E1D8] bg-[#FFFDF8] p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[3px] text-[#8B8175]">
            Visual Output
          </p>

          <h3 className="mt-1 text-2xl font-black text-[#171615]">
            {config.label}
          </h3>
        </div>

        <span className="rounded-full bg-[#F0ECE4] px-4 py-2 text-xs font-semibold text-[#6F675E]">
          {config.width} × {config.height}
        </span>
      </div>

      <div className="overflow-auto rounded-[24px] bg-[#EDE8DE] p-5">
  <div
    style={{
      width: `${config.width * config.previewScale}px`,
      height: `${config.height * config.previewScale}px`,
    }}
    className="mx-auto overflow-hidden rounded-[20px] shadow-xl"
  >
    <div
      style={{
        width: `${config.width}px`,
        height: `${config.height}px`,
        transform: `scale(${config.previewScale})`,
        transformOrigin: "top left",
      }}
    >
      <div
        ref={cardRef}
        style={{
          width: `${config.width}px`,
          height: `${config.height}px`,
        }}
      >
        {renderDesign()}
      </div>
    </div>
  </div>
</div>

<div className="mt-5 flex flex-wrap gap-3">
  <button
    onClick={downloadPng}
    className="rounded-2xl bg-[#171615] px-5 py-3 font-semibold text-white transition hover:bg-[#302D29]"
  >
    Download PNG
  </button>

  <button
    onClick={downloadPdf}
    className="rounded-2xl border border-[#171615] bg-white px-5 py-3 font-semibold text-[#171615] transition hover:bg-[#F2EEE6]"
  >
    Download PDF
  </button>

  <button
    onClick={printCard}
    className="rounded-2xl border border-[#D9D2C7] bg-white px-5 py-3 font-semibold text-[#171615] transition hover:bg-[#F5F2EA]"
  >
    Print
  </button>
    </div>
    </div>
  );
}
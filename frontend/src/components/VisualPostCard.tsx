"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";

type Platform = "linkedin" | "instagram" | "x";

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
    previewScale: 0.3,
  },
  x: {
    width: 1600,
    height: 900,
    label: "X",
    previewScale: 0.28,
  },
};

export default function VisualPostCard({
  platform,
  headline,
  content,
  imageUrl,
  source,
}: VisualPostCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const config = platformConfig[platform];

  async function downloadPng() {
    if (!cardRef.current) return;

    try {
      const dataUrl = await toPng(cardRef.current, {
        cacheBust: true,
        pixelRatio: 1,
      });

      const link = document.createElement("a");
      link.download = `${platform}-visual-post.png`;
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error("PNG export failed:", error);
      alert("Could not export PNG.");
    }
  }

  function printCard() {
    if (!cardRef.current) return;

    const printWindow = window.open("", "_blank");

    if (!printWindow) {
      alert("Please allow popups to print this design.");
      return;
    }

    printWindow.document.write(`
      <html>
        <head>
          <title>${config.label} Visual Post</title>
          <style>
            body {
              margin: 0;
              display: flex;
              justify-content: center;
              align-items: center;
              background: white;
            }
          </style>
        </head>
        <body>
          ${cardRef.current.outerHTML}
        </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  }

  return (
    <div className="rounded-[32px] border border-[#E7E1D8] bg-[#FFFDF8] p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[3px] text-[#8B8175]">
            Visual Output
          </p>

          <h3 className="mt-1 text-2xl font-black text-[#171615]">
            {config.label} Post
          </h3>
        </div>

        <span className="rounded-full bg-[#F0ECE4] px-4 py-2 text-xs font-semibold text-[#6F675E]">
          {config.width} × {config.height}
        </span>
      </div>

      <div className="overflow-auto rounded-[24px] bg-[#EEE9DF] p-5">
        <div
          style={{
            width: `${config.width * config.previewScale}px`,
            height: `${config.height * config.previewScale}px`,
          }}
          className="mx-auto overflow-hidden rounded-[20px] shadow-xl"
        >
          <div
            ref={cardRef}
            style={{
              width: `${config.width}px`,
              height: `${config.height}px`,
              transform: `scale(${config.previewScale})`,
              transformOrigin: "top left",
              backgroundImage: imageUrl
                ? `linear-gradient(
                    180deg,
                    rgba(16, 23, 20, 0.08) 0%,
                    rgba(16, 23, 20, 0.9) 82%
                  ),
                  url("${imageUrl}")`
                : `linear-gradient(
                    145deg,
                    #EFE7D8 0%,
                    #DDE7E0 50%,
                    #BCCFC5 100%
                  )`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
            className="relative overflow-hidden p-16 text-white"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/70" />

            <div className="relative z-10 flex h-full flex-col justify-between">
              <div className="flex items-center justify-between">
                <p className="text-2xl font-semibold tracking-[0.28em]">
                  AI CONTENT OS
                </p>

                <p className="rounded-full border border-white/40 bg-black/20 px-6 py-3 text-xl font-semibold tracking-[0.2em] backdrop-blur-md">
                  {config.label}
                </p>
              </div>

              <div className="max-w-[88%]">
                <p className="mb-7 text-2xl uppercase tracking-[0.25em] text-white/75">
                  Intelligence Brief
                </p>

                <h2
                  className="mb-8 text-7xl leading-[0.98]"
                  style={{ fontFamily: "Instrument Serif" }}
                >
                  {headline}
                </h2>

                <p className="max-w-[90%] text-3xl leading-relaxed text-white/90">
                  {content}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-white/25 pt-7 text-xl text-white/75">
                <p>{source || "AI Content OS"}</p>
                <p>AI • Telecom • Marketing</p>
              </div>
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
          onClick={printCard}
          className="rounded-2xl border border-[#D9D2C7] bg-white px-5 py-3 font-semibold text-[#171615] transition hover:bg-[#F5F2EA]"
        >
          Print
        </button>
      </div>
    </div>
  );
}
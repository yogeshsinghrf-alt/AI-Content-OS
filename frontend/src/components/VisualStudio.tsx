"use client";

import { useState } from "react";
import VisualPostCard from "./VisualPostCard";

type VisualStudioProps = {
  headline?: string;
  linkedinText?: string;
  instagramText?: string;
  xText?: string;
  linkedinImage?: string;
  instagramImage?: string;
  xImage?: string;
  source?: string;
};

type Platform = "linkedin" | "instagram" | "x";

export default function VisualStudio({
  headline = "AI is reshaping how businesses create and communicate",
  linkedinText = "",
  instagramText = "",
  xText = "",
  linkedinImage,
  instagramImage,
  xImage,
  source,
}: VisualStudioProps) {
  const [activePlatform, setActivePlatform] =
    useState<Platform>("linkedin");

  const platformData = {
    linkedin: {
      label: "LinkedIn",
      content: linkedinText,
      image: linkedinImage,
    },
    instagram: {
      label: "Instagram",
      content: instagramText,
      image: instagramImage,
    },
    x: {
      label: "X",
      content: xText,
      image: xImage,
    },
  };

  const active = platformData[activePlatform];

  return (
    <section className="mt-10 rounded-[36px] border border-[#E7E1D8] bg-[#F8F4EC] p-8 shadow-sm">
      <div className="mb-7 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[4px] text-[#8B8175]">
            Visual Studio
          </p>

          <h2
            className="mt-2 text-5xl text-[#171615]"
            style={{ fontFamily: "Instrument Serif" }}
          >
            Platform-ready designs
          </h2>

          <p className="mt-3 max-w-2xl text-[#6F675E]">
            Preview, download and print visual posts created for
            LinkedIn, Instagram and X.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 rounded-2xl border border-[#DED7CB] bg-[#FFFDF8] p-2">
          {(
            [
              ["linkedin", "LinkedIn"],
              ["instagram", "Instagram"],
              ["x", "X"],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              onClick={() => setActivePlatform(value)}
              className={`rounded-xl px-5 py-3 text-sm font-semibold transition ${
                activePlatform === value
                  ? "bg-[#171615] text-white shadow-sm"
                  : "text-[#6F675E] hover:bg-[#F2EEE6]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <VisualPostCard
        platform={activePlatform}
        headline={headline}
        content={active.content}
        imageUrl={active.image}
        source={source}
      />
    </section>
  );
}
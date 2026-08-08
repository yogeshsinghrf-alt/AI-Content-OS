"use client";

import { useState } from "react";
import VisualPostCard from "./VisualPostCard";

type Platform =
  | "linkedin"
  | "instagram"
  | "x"
  | "carousel"
  | "infographic"
  | "quote";

type VisualStudioProps = {
  headline?: string;

  linkedinText?: string;
  instagramText?: string;
  xText?: string;

  carouselText?: string;
  infographicText?: string;
  quoteText?: string;

  linkedinImage?: string;
  instagramImage?: string;
  xImage?: string;

  carouselImage?: string;
  infographicImage?: string;
  quoteImage?: string;

  source?: string;
};

export default function VisualStudio({
  headline = "AI Intelligence Brief",

  linkedinText = "",
  instagramText = "",
  xText = "",

  carouselText = "",
  infographicText = "",
  quoteText = "",

  linkedinImage,
  instagramImage,
  xImage,

  carouselImage,
  infographicImage,
  quoteImage,

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

    carousel: {
      label: "Carousel",
      content:
        carouselText ||
        "Swipe through the key ideas, business implications and practical takeaways.",
      image: carouselImage || linkedinImage,
    },

    infographic: {
      label: "Infographic",
      content:
        infographicText ||
        "Key statistics, insights and implications presented in a visual format.",
      image: infographicImage || instagramImage,
    },

    quote: {
      label: "Quote Card",
      content:
        quoteText ||
        "A strong insight designed for professional social sharing.",
      image: quoteImage || xImage,
    },
  };

  const active = platformData[activePlatform];

  return (
    <section className="mt-10 rounded-[36px] border border-[#E7E1D8] bg-[#F8F4EC] p-8 shadow-sm">
      <div className="mb-7">
        <p className="text-xs uppercase tracking-[4px] text-[#8B8175]">
          Visual Studio
        </p>

        <h2
          className="mt-2 text-5xl text-[#171615]"
          style={{ fontFamily: "Instrument Serif" }}
        >
          Publication-ready creative assets
        </h2>

        <p className="mt-3 max-w-3xl text-[#6F675E]">
          Preview, download and print platform-specific social
          graphics, carousel covers, infographics and quote cards.
        </p>
      </div>

      <div className="mb-7 flex flex-wrap gap-2 rounded-2xl border border-[#DED7CB] bg-[#FFFDF8] p-2">
        {(
          [
            ["linkedin", "LinkedIn"],
            ["instagram", "Instagram"],
            ["x", "X"],
            ["carousel", "Carousel"],
            ["infographic", "Infographic"],
            ["quote", "Quote"],
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

      <VisualPostCard
        platform={activePlatform}
        headline={
          activePlatform === "quote"
            ? "An idea worth remembering"
            : headline
        }
        content={active.content}
        imageUrl={active.image}
        source={source}
      />
    </section>
  );
}
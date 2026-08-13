"use client";

import { useState } from "react";
import VisualPostCard from "./VisualPostCard";
import InfographicCard from "./InfographicCard";
import QuoteCard from "./QuoteCard";

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
  infographicPoints?: string[];
  quoteText?: string;

  linkedinImage?: string;
  instagramImage?: string;
  xImage?: string;

  carouselImage?: string;
  infographicImage?: string;
  quoteImage?: string;

  source?: string;
  packageId?: string;
};

const PLATFORM_META: Record<
  Platform,
  {
    label: string;
    eyebrow: string;
    description: string;
  }
> = {
  linkedin: {
    label: "LinkedIn",
    eyebrow: "Executive Editorial",
    description:
      "Professional square creative for business and thought-leadership publishing.",
  },

  instagram: {
    label: "Instagram",
    eyebrow: "Visual Magazine",
    description:
      "Portrait-first editorial creative with stronger imagery and shorter display copy.",
  },

  x: {
    label: "X",
    eyebrow: "News Brief",
    description:
      "Wide, fast-scanning visual designed around one strong insight.",
  },

  carousel: {
    label: "Carousel",
    eyebrow: "Swipe Story",
    description:
      "Editorial cover concept for a multi-slide educational or insight carousel.",
  },

  infographic: {
    label: "Infographic",
    eyebrow: "Data Story",
    description:
      "Structured visual summary for key takeaways, numbers and business implications.",
  },

  quote: {
    label: "Quote",
    eyebrow: "Insight Card",
    description:
      "Minimal shareable visual focused on one memorable statement.",
  },
};

export default function VisualStudio({
  headline = "AI Intelligence Brief",

  linkedinText = "",
  instagramText = "",
  xText = "",

  carouselText = "",
  infographicText = "",
  infographicPoints = [],
  quoteText = "",

  linkedinImage,
  instagramImage,
  xImage,

  carouselImage,
  infographicImage,
  quoteImage,

  source,
  packageId,
}: VisualStudioProps) {
  const [activePlatform, setActivePlatform] =
    useState<Platform>("linkedin");

  const platformData: Record<
    Platform,
    {
      content: string;
      image?: string;
    }
  > = {
    linkedin: {
      content: linkedinText,
      image: linkedinImage,
    },

    instagram: {
      content: instagramText,
      image: instagramImage,
    },

    x: {
      content: xText,
      image: xImage,
    },

    carousel: {
      content:
        carouselText ||
        "Swipe through the key ideas, implications and practical takeaways.",
      image:
        carouselImage ||
        linkedinImage,
    },

    infographic: {
      content:
        infographicText ||
        "Key statistics, insights and implications presented in a visual format.",
      image:
        infographicImage ||
        instagramImage,
    },

    quote: {
      content:
        quoteText ||
        "A strong idea designed for professional social sharing.",
      image:
        quoteImage ||
        xImage,
    },
  };

  const active = platformData[activePlatform];
  const meta = PLATFORM_META[activePlatform];

  return (
    <section className="mt-12 overflow-hidden rounded-[40px] border border-[#E5DED2] bg-[#F7F3EB] shadow-[0_18px_60px_rgba(70,60,45,0.08)]">

      {/* Header */}
      <div className="border-b border-[#E4DDD2] px-8 py-9 lg:px-10">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">

          <div>
            <p className="text-xs font-semibold uppercase tracking-[4px] text-[#8A7E70]">
              Creative Studio
            </p>

            <h2
              className="mt-3 text-4xl leading-none text-[#171615] md:text-5xl"
              style={{
                fontFamily: "Instrument Serif",
              }}
            >
              Publication-ready social assets
            </h2>

            <p className="mt-4 max-w-3xl text-base leading-7 text-[#6E655C]">
              One story, translated into platform-specific
              creative formats for LinkedIn, Instagram, X,
              carousels, infographics and quote cards.
            </p>
          </div>

          <div className="rounded-full border border-[#DDD5C9] bg-[#FFFDF9] px-5 py-3 text-sm text-[#6C635A]">
            6 creative formats
          </div>
        </div>
      </div>

      {/* Platform navigation */}
      <div className="px-8 pt-7 lg:px-10">
        <div className="flex flex-wrap gap-2">
          {(
            [
              "linkedin",
              "instagram",
              "x",
              "carousel",
              "infographic",
              "quote",
            ] as Platform[]
          ).map((platform) => {
            const item = PLATFORM_META[platform];

            return (
              <button
                key={platform}
                onClick={() =>
                  setActivePlatform(platform)
                }
                className={`rounded-full border px-5 py-3 text-sm font-semibold transition ${
                  activePlatform === platform
                    ? "border-[#171615] bg-[#171615] text-white shadow-sm"
                    : "border-[#DED7CC] bg-[#FFFDF9] text-[#675F57] hover:border-[#BEB4A5] hover:bg-white"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Active design info */}
      <div className="px-8 pb-4 pt-8 lg:px-10">
        <div className="flex flex-col gap-3 border-l-2 border-[#B6A58F] pl-5">
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#927F68]">
            {meta.eyebrow}
          </p>

          <h3 className="text-2xl font-bold text-[#191817]">
            {meta.label} Creative
          </h3>

          <p className="max-w-3xl text-sm leading-6 text-[#756C63]">
            {meta.description}
          </p>
        </div>
      </div>

      {/* Design preview */}
<div className="px-8 pb-10 pt-4 lg:px-10">
  {activePlatform === "infographic" ? (
    <InfographicCard
      headline={headline}
      subtitle={infographicText}
      points={infographicPoints}
      source={source}
      packageId={packageId}
    />
  ) : activePlatform === "quote" ? (
    <QuoteCard
      quote={quoteText}
      source={source}
    />
  ) : (
    <VisualPostCard
      platform={activePlatform}
      headline={headline}
      content={active.content}
      imageUrl={active.image}
      source={source}
    />
  )}
</div>
</section>
);
}
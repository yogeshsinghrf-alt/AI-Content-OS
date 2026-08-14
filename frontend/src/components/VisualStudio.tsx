"use client";

import { useState } from "react";
import VisualPostCard from "./VisualPostCard";
import InfographicCard from "./InfographicCard";

type SocialPlatform =
  | "linkedin"
  | "instagram"
  | "x";

type StudioPlatform =
  | SocialPlatform
  | "infographic"
  | "carousel";

type SocialCreative = {
  headline: string;
  content: string;
  image?: string;
  source: string;
};

type VisualStudioProps = {
  linkedin1: SocialCreative;
  linkedin2: SocialCreative;
  instagram1: SocialCreative;
  instagram2: SocialCreative;
  x1: SocialCreative;
  x2: SocialCreative;

  infographic: {
    headline: string;
    subtitle: string;
    points: string[];
    source: string;
  };

  carousel: {
    headline: string;
    source: string;
  };

  packageId?: string;
};

const PLATFORM_META: Record<
  StudioPlatform,
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
      "Two independently sourced business creatives for professional publishing.",
  },
  instagram: {
    label: "Instagram",
    eyebrow: "Visual Magazine",
    description:
      "Two independently sourced portrait-first editorial creatives.",
  },
  x: {
    label: "X",
    eyebrow: "News Brief",
    description:
      "Two independently sourced wide creatives designed for fast scanning.",
  },
  infographic: {
    label: "Infographic",
    eyebrow: "Data Story",
    description:
      "A dedicated story rendered as a structured four-point visual summary.",
  },
  carousel: {
    label: "Carousel",
    eyebrow: "Swipe Story",
    description:
      "A dedicated story transformed into a six-slide editorial narrative.",
  },
};

export default function VisualStudio({
  linkedin1,
  linkedin2,
  instagram1,
  instagram2,
  x1,
  x2,
  infographic,
  carousel,
  packageId,
}: VisualStudioProps) {
  const [activePlatform, setActivePlatform] =
    useState<StudioPlatform>("linkedin");

  const [activeOption, setActiveOption] =
    useState<1 | 2>(1);

  const socialMap = {
    linkedin: {
      1: linkedin1,
      2: linkedin2,
    },
    instagram: {
      1: instagram1,
      2: instagram2,
    },
    x: {
      1: x1,
      2: x2,
    },
  };

  const isSocial =
    activePlatform === "linkedin" ||
    activePlatform === "instagram" ||
    activePlatform === "x";

  const activeSocial = isSocial
    ? socialMap[activePlatform][activeOption]
    : null;

  const meta =
    PLATFORM_META[activePlatform];

  return (
    <section className="mt-12 overflow-hidden rounded-[40px] border border-[#E5DED2] bg-[#F7F3EB] shadow-[0_18px_60px_rgba(70,60,45,0.08)]">

      <div className="border-b border-[#E4DDD2] px-8 py-9 lg:px-10">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[4px] text-[#8A7E70]">
              Creative Studio
            </p>

            <h2
              className="mt-3 text-4xl leading-none text-[#171615] md:text-5xl"
              style={{
                fontFamily:
                  "Instrument Serif",
              }}
            >
              Multi-story editorial assets
            </h2>

            <p className="mt-4 max-w-3xl text-base leading-7 text-[#6E655C]">
              Six social creatives plus a dedicated infographic and carousel, each grounded in its assigned news story.
            </p>
          </div>

          <div className="rounded-full border border-[#DDD5C9] bg-[#FFFDF9] px-5 py-3 text-sm text-[#6C635A]">
            8 story outputs
          </div>
        </div>
      </div>

      <div className="px-8 pt-7 lg:px-10">
        <div className="flex flex-wrap gap-2">
          {(
            [
              "linkedin",
              "instagram",
              "x",
              "infographic",
              "carousel",
            ] as StudioPlatform[]
          ).map((platform) => {
            const item =
              PLATFORM_META[platform];

            return (
              <button
                key={platform}
                onClick={() => {
                  setActivePlatform(
                    platform
                  );

                  if (
                    platform ===
                      "linkedin" ||
                    platform ===
                      "instagram" ||
                    platform === "x"
                  ) {
                    setActiveOption(1);
                  }
                }}
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

        {isSocial && (
          <div className="mt-4 flex gap-2">
            {[1, 2].map((option) => (
              <button
                key={option}
                onClick={() =>
                  setActiveOption(
                    option as 1 | 2
                  )
                }
                className={`rounded-full px-4 py-2 text-xs font-semibold ${
                  activeOption === option
                    ? "bg-[#9A8167] text-white"
                    : "border border-[#D8CFC2] bg-white text-[#6E655C]"
                }`}
              >
                Option {option}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="px-8 pb-4 pt-8 lg:px-10">
        <div className="flex flex-col gap-3 border-l-2 border-[#B6A58F] pl-5">
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#927F68]">
            {meta.eyebrow}
          </p>

          <h3 className="text-2xl font-bold text-[#191817]">
            {meta.label}
            {isSocial
              ? ` Creative ${activeOption}`
              : ""}
          </h3>

          <p className="max-w-3xl text-sm leading-6 text-[#756C63]">
            {meta.description}
          </p>
        </div>
      </div>

      <div className="px-8 pb-10 pt-4 lg:px-10">
        {activePlatform ===
        "infographic" ? (
          <InfographicCard
            headline={
              infographic.headline
            }
            subtitle={
              infographic.subtitle
            }
            points={
              infographic.points
            }
            source={
              infographic.source
            }
            packageId={packageId}
          />
        ) : activePlatform ===
          "carousel" ? (
          <div className="rounded-[28px] border border-[#DDD4C8] bg-[#FFFDF9] p-8">
            <p className="text-xs font-bold uppercase tracking-[3px] text-[#927F68]">
              Dedicated Carousel Story
            </p>
            <h3
              className="mt-3 text-4xl text-[#171615]"
              style={{
                fontFamily:
                  "Instrument Serif",
              }}
            >
              {carousel.headline}
            </h3>
            <p className="mt-4 text-sm text-[#756C63]">
              Source: {carousel.source}
            </p>
            <p className="mt-5 text-sm leading-6 text-[#5F574F]">
              View the full six-slide carousel below.
            </p>
          </div>
        ) : activeSocial ? (
          <VisualPostCard
            platform={
              activePlatform as SocialPlatform
            }
            headline={
              activeSocial.headline
            }
            content={
              activeSocial.content
            }
            imageUrl={
              activeSocial.image
            }
            source={
              activeSocial.source
            }
          />
        ) : null}
      </div>
    </section>
  );
}

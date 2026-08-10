"use client";

import { useState } from "react";

type Platform = "linkedin" | "x" | "instagram";

type SocialContentTabsProps = {
  linkedin1?: string;
  linkedin2?: string;
  x1?: string;
  x2?: string;
  instagram1?: string;
  instagram2?: string;
};

export default function SocialContentTabs({
  linkedin1 = "",
  linkedin2 = "",
  x1 = "",
  x2 = "",
  instagram1 = "",
  instagram2 = "",
}: SocialContentTabsProps) {
  const [platform, setPlatform] =
    useState<Platform>("linkedin");

  const content = {
    linkedin: {
      label: "LinkedIn",
      description:
        "Professional business and thought-leadership copy.",
      option1: linkedin1,
      option2: linkedin2,
    },

    x: {
      label: "X",
      description:
        "Concise, fast-scanning social updates.",
      option1: x1,
      option2: x2,
    },

    instagram: {
      label: "Instagram",
      description:
        "Visual-first captions with a more conversational tone.",
      option1: instagram1,
      option2: instagram2,
    },
  };

  const active = content[platform];

  async function copyText(text: string) {
    await navigator.clipboard.writeText(text);
    alert("Copied!");
  }

  return (
    <section className="mt-10 rounded-[32px] border border-[#E4DDD2] bg-[#FFFDF9] p-7 shadow-sm lg:p-9">

      {/* Header */}
      <div className="mb-7">
        <p className="text-xs font-bold uppercase tracking-[4px] text-[#928575]">
          Social Copy Studio
        </p>

        <h2
          className="mt-2 text-4xl text-[#171615]"
          style={{
            fontFamily: "Instrument Serif",
          }}
        >
          Platform-ready posts
        </h2>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-[#746B62]">
          Two writing options for each social platform.
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-7 flex flex-wrap gap-2 rounded-2xl border border-[#E2DBD0] bg-[#F6F2EA] p-2">

        {(
          [
            ["linkedin", "LinkedIn"],
            ["x", "X"],
            ["instagram", "Instagram"],
          ] as const
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() =>
              setPlatform(value)
            }
            className={`rounded-xl px-5 py-3 text-sm font-semibold transition ${
              platform === value
                ? "bg-[#171615] text-white shadow-sm"
                : "text-[#675F57] hover:bg-white"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Platform heading */}
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">

        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#998875]">
            {active.label}
          </p>

          <p className="mt-1 text-sm text-[#776E65]">
            {active.description}
          </p>
        </div>

        <span className="rounded-full border border-[#DDD5C9] bg-white px-4 py-2 text-xs text-[#756C63]">
          2 options
        </span>
      </div>

      {/* Options */}
      <div className="grid gap-5 lg:grid-cols-2">

        <PostOption
          number="01"
          content={active.option1}
          onCopy={copyText}
        />

        <PostOption
          number="02"
          content={active.option2}
          onCopy={copyText}
        />

      </div>
    </section>
  );
}


function PostOption({
  number,
  content,
  onCopy,
}: {
  number: string;
  content: string;
  onCopy: (text: string) => void;
}) {
  return (
    <article className="flex min-h-[280px] flex-col rounded-[24px] border border-[#E5DED3] bg-white p-6">

      <div className="flex items-center justify-between">

        <span
          className="text-4xl text-[#C8B9A5]"
          style={{
            fontFamily: "Instrument Serif",
          }}
        >
          {number}
        </span>

        <button
          type="button"
          onClick={() =>
            onCopy(content)
          }
          className="rounded-full bg-[#171615] px-4 py-2 text-xs font-semibold text-white hover:bg-[#302D29]"
        >
          Copy
        </button>
      </div>

      <div className="mt-6 flex-1 whitespace-pre-wrap text-sm leading-7 text-[#514A43]">
        {content || "No content generated."}
      </div>

    </article>
  );
}
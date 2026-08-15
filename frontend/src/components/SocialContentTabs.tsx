"use client";

import {
  useRef,
  useState,
} from "react";

import { toPng } from "html-to-image";


type Platform =
  | "linkedin"
  | "x"
  | "instagram";


type StoryMeta = {
  source: string;
  title: string;
  link: string;
};


type SocialContentTabsProps = {
  linkedin1?: string;
  linkedin2?: string;

  x1?: string;
  x2?: string;

  instagram1?: string;
  instagram2?: string;

  linkedinStory1: StoryMeta;
  linkedinStory2: StoryMeta;

  xStory1: StoryMeta;
  xStory2: StoryMeta;

  instagramStory1: StoryMeta;
  instagramStory2: StoryMeta;
};


export default function SocialContentTabs({
  linkedin1 = "",
  linkedin2 = "",

  x1 = "",
  x2 = "",

  instagram1 = "",
  instagram2 = "",

  linkedinStory1,
  linkedinStory2,

  xStory1,
  xStory2,

  instagramStory1,
  instagramStory2,
}: SocialContentTabsProps) {
  const [platform, setPlatform] =
    useState<Platform>(
      "linkedin"
    );


  const content = {
    linkedin: {
      label: "LinkedIn",

      description:
        "Two independent business and thought-leadership stories.",

      option1: linkedin1,
      option2: linkedin2,

      story1:
        linkedinStory1,

      story2:
        linkedinStory2,
    },

    x: {
      label: "X",

      description:
        "Two independent fast-scanning news stories.",

      option1: x1,
      option2: x2,

      story1:
        xStory1,

      story2:
        xStory2,
    },

    instagram: {
      label: "Instagram",

      description:
        "Two independent visual-first editorial stories.",

      option1:
        instagram1,

      option2:
        instagram2,

      story1:
        instagramStory1,

      story2:
        instagramStory2,
    },
  };


  const active =
    content[platform];


  async function copyText(
    text: string
  ) {
    await navigator.clipboard.writeText(
      text
    );

    alert("Copied!");
  }


  return (
    <section className="mt-10 rounded-[32px] border border-[#E4DDD2] bg-[#FFFDF9] p-7 shadow-sm lg:p-9">

      {/* ----------------------------------
          SECTION HEADER
      ---------------------------------- */}

      <div className="mb-7">
        <p className="text-xs font-bold uppercase tracking-[4px] text-[#928575]">
          Social Copy Studio
        </p>

        <h2
          className="mt-2 text-4xl text-[#171615]"
          style={{
            fontFamily:
              "Instrument Serif",
          }}
        >
          Platform-ready posts
        </h2>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-[#746B62]">
          Each option is grounded in a different assigned article.
        </p>
      </div>


      {/* ----------------------------------
          PLATFORM TABS
      ---------------------------------- */}

      <div className="mb-7 flex flex-wrap gap-2 rounded-2xl border border-[#E2DBD0] bg-[#F6F2EA] p-2">

        {(
          [
            [
              "linkedin",
              "LinkedIn",
            ],

            [
              "x",
              "X",
            ],

            [
              "instagram",
              "Instagram",
            ],
          ] as const
        ).map(
          ([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() =>
                setPlatform(
                  value
                )
              }
              className={`rounded-xl px-5 py-3 text-sm font-semibold transition ${
                platform ===
                value
                  ? "bg-[#171615] text-white shadow-sm"
                  : "text-[#675F57] hover:bg-white"
              }`}
            >
              {label}
            </button>
          )
        )}

      </div>


      {/* ----------------------------------
          ACTIVE PLATFORM INFO
      ---------------------------------- */}

      <div className="mb-7 flex flex-wrap items-end justify-between gap-4">

        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#998875]">
            {active.label}
          </p>

          <p className="mt-1 text-sm text-[#776E65]">
            {
              active.description
            }
          </p>
        </div>


        <span className="rounded-full border border-[#DDD5C9] bg-white px-4 py-2 text-xs text-[#756C63]">
          2 independent stories
        </span>

      </div>


      {/* ----------------------------------
          TWO INDEPENDENT STORIES
      ---------------------------------- */}

      <div className="grid gap-8 lg:grid-cols-2">

        <PostOption
          number="01"
          platform={
            platform
          }
          content={
            active.option1
          }
          story={
            active.story1
          }
          onCopy={
            copyText
          }
        />


        <PostOption
          number="02"
          platform={
            platform
          }
          content={
            active.option2
          }
          story={
            active.story2
          }
          onCopy={
            copyText
          }
        />

      </div>

    </section>
  );
}


function PostOption({
  number,
  platform,
  content,
  story,
  onCopy,
}: {
  number: string;

  platform:
    Platform;

  content: string;

  story:
    StoryMeta;

  onCopy:
    (
      text: string
    ) => void;
}) {

  /*
   * IMPORTANT:
   *
   * exportRef points ONLY at the
   * rectangular story card.
   *
   * Number, Copy button and Download PNG
   * button live outside this ref and therefore
   * never appear in the exported PNG.
   */

  const exportRef =
    useRef<HTMLDivElement | null>(
      null
    );


  async function downloadPng() {
    if (
      !exportRef.current
    ) {
      return;
    }


    try {
      const dataUrl =
        await toPng(
          exportRef.current,
          {
            cacheBust:
              true,

            pixelRatio:
              2,

            backgroundColor:
              "#FFFFFF",
          }
        );


      const link =
        document.createElement(
          "a"
        );


      const safeSource =
        (
          story.source ||
          "story"
        )
          .toLowerCase()
          .replace(
            /[^a-z0-9]+/g,
            "-"
          )
          .replace(
            /^-|-$/g,
            ""
          );


      link.download =
        `AI-Content-OS-${platform}-${number}-${safeSource}.png`;


      link.href =
        dataUrl;


      document.body.appendChild(
        link
      );


      link.click();


      document.body.removeChild(
        link
      );

    } catch (error) {

      console.error(
        "Social post PNG export failed:",
        error
      );


      alert(
        "Could not export this story as PNG."
      );
    }
  }


  return (
    <div className="min-w-0">

      {/* ----------------------------------
          OUTSIDE EXPORT BOUNDARY
      ---------------------------------- */}

      <div className="mb-3 flex flex-wrap items-center justify-between gap-3 px-1">

        <span
          className="text-4xl text-[#A9815D]"
          style={{
            fontFamily:
              "Instrument Serif",
          }}
        >
          {number}
        </span>


        <div className="flex flex-wrap items-center gap-2">

          <button
            type="button"
            onClick={() =>
              onCopy(
                content
              )
            }
            className="rounded-full bg-[#171615] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#302D29]"
          >
            Copy
          </button>


          <button
            type="button"
            onClick={
              downloadPng
            }
            className="rounded-full border border-[#CDBAA7] bg-[#FFFDF9] px-4 py-2 text-xs font-semibold text-[#76583E] transition hover:bg-[#F6F0E8]"
          >
            ↓ Download PNG
          </button>

        </div>

      </div>


      {/* ==================================
          PNG EXPORT BOUNDARY STARTS HERE
          ONLY THIS RECTANGLE IS EXPORTED
      ================================== */}

      <div
        ref={exportRef}
        className={`flex flex-col overflow-hidden rounded-[24px] border border-[#E5DED3] bg-white p-7 ${
        platform === "linkedin"
          ? "aspect-square"
          : "min-h-[420px]"
      }`}
      style={{
      borderRadius: "24px",
      backgroundColor: "#FFFFFF",
      color: "#514A43",
      }}
  >

        {/* Story identity panel */}

        <div className="rounded-[18px] bg-[#F7F3EC] p-5">

          <p className="text-[10px] font-bold uppercase tracking-[2.5px] text-[#9A6F4C]">
            {
              story.source
            }
          </p>


          <p className="mt-2 text-base font-semibold leading-6 text-[#27231F]">
            {
              story.title
            }
          </p>


          {story.link && (
            <a
              href={
                story.link
              }
              target="_blank"
              rel="noreferrer"
              className="mt-2 inline-block text-xs font-semibold text-[#78644E] underline"
            >
              Read source
            </a>
          )}

        </div>


        {/* Generated social story */}

        <div className="mt-6 flex-1 whitespace-pre-wrap text-sm leading-7 text-[#514A43]">
          {
            content ||
            "No content generated."
          }
        </div>

      </div>

      {/* ==================================
          PNG EXPORT BOUNDARY ENDS HERE
      ================================== */}

    </div>
  );
}
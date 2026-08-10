"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

type CarouselDeckProps = {
  headline: string;
  subtitle?: string;
  points?: string[];
  source?: string;
  imageUrl?: string;
};

function shortenText(text: string, limit: number) {
  if (!text) return "";

  return text.length > limit
    ? `${text.slice(0, limit).trim()}…`
    : text;
}

export default function CarouselDeck({
  headline,
  subtitle = "",
  points = [],
  source = "AI Content OS",
  imageUrl,
}: CarouselDeckProps) {
  const slideRefs =
    useRef<(HTMLDivElement | null)[]>([]);

  const safePoints = [
    points[0] ||
      "Understand the development shaping the market.",
    points[1] ||
      "Evaluate why this matters for business and technology.",
    points[2] ||
      "Watch adoption, execution and competitive response.",
    points[3] ||
      "Identify where measurable business value may emerge.",
  ];

  const slides = [
    {
      number: "01",
      eyebrow: "THE BRIEF",
      title: headline,
      body:
        subtitle ||
        "A concise look at the development shaping today's technology landscape.",
    },
    {
      number: "02",
      eyebrow: "WHAT HAPPENED",
      title: "The development",
      body: safePoints[0],
    },
    {
      number: "03",
      eyebrow: "WHY IT MATTERS",
      title: "The bigger picture",
      body: safePoints[1],
    },
    {
      number: "04",
      eyebrow: "WHAT TO WATCH",
      title: "The next signal",
      body: safePoints[2],
    },
    {
      number: "05",
      eyebrow: "BUSINESS IMPACT",
      title: "Where value may emerge",
      body: safePoints[3],
    },
    {
      number: "06",
      eyebrow: "TAKEAWAY",
      title: "The signal behind the noise",
      body:
        "Follow the technology, but focus on where it creates measurable business value.",
    },
  ];

  async function createSlidePng(
    index: number
  ) {
    const slide =
      slideRefs.current[index];

    if (!slide) {
      throw new Error(
        "Carousel slide not found."
      );
    }

    return await toPng(slide, {
      cacheBust: true,
      pixelRatio: 2,
      backgroundColor: "#F7F1E7",
    });
  }

  async function downloadSlide(
    index: number
  ) {
    try {
      const dataUrl =
        await createSlidePng(index);

      const link =
        document.createElement("a");

      link.download =
        `carousel-slide-${index + 1}.png`;

      link.href = dataUrl;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error(
        "Carousel PNG export failed:",
        error
      );

      alert(
        "Could not download this slide."
      );
    }
  }

  async function downloadCarouselPdf() {
    try {
      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: [216, 216],
      });

      for (
        let index = 0;
        index < slides.length;
        index++
      ) {
        const dataUrl =
          await createSlidePng(index);

        if (index > 0) {
          pdf.addPage(
            [216, 216],
            "portrait"
          );
        }

        pdf.addImage(
          dataUrl,
          "PNG",
          0,
          0,
          216,
          216,
          undefined,
          "FAST"
        );
      }

      pdf.save(
        "AI-Content-OS-carousel.pdf"
      );
    } catch (error) {
      console.error(
        "Carousel PDF export failed:",
        error
      );

      alert(
        "Could not download carousel PDF."
      );
    }
  }

  return (
    <section className="rounded-[32px] border border-[#E2DBD0] bg-[#FFFDF9] p-7 shadow-sm lg:p-9">

      {/* HEADER */}

      <div className="mb-7 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">

        <div>
          <p className="text-xs font-bold uppercase tracking-[4px] text-[#927F68]">
            Carousel Studio
          </p>

          <h2
            className="mt-2 text-4xl text-[#171615]"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            6-slide editorial carousel
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-[#6F675E]">
            A publication-style story designed
            for LinkedIn and Instagram.
          </p>
        </div>

        <button
          onClick={downloadCarouselPdf}
          className="w-fit rounded-2xl bg-[#171615] px-5 py-3 text-sm font-semibold text-white hover:bg-[#302D29]"
        >
          Download Full Carousel PDF
        </button>
      </div>

      {/* SLIDES */}

      <div className="grid gap-8 xl:grid-cols-2">

        {slides.map((slide, index) => (

          <div
            key={slide.number}
            className="flex flex-col"
          >

            {/* 540×540 preview = 1080×1080 export */}

            <div
              style={{
                width: "540px",
                height: "540px",
              }}
              className="mx-auto max-w-full"
            >

              <div
                ref={(element) => {
                  slideRefs.current[index] =
                    element;
                }}
                style={{
                  width: "540px",
                  height: "540px",
                  margin: 0,
                  boxSizing: "border-box",
                }}
                className="relative flex flex-col overflow-hidden bg-[#F7F1E7]"
              >

                {/* SLIDE 1 — COVER */}

                {index === 0 && (
                  <>
                    {imageUrl && (
                      <img
                        src={imageUrl}
                        alt=""
                        className="absolute inset-0 h-full w-full object-cover"
                        crossOrigin="anonymous"
                      />
                    )}

                    <div
                      className={`absolute inset-0 ${
                        imageUrl
                          ? "bg-gradient-to-t from-black/85 via-black/30 to-black/15"
                          : "bg-gradient-to-br from-[#17211C] via-[#344139] to-[#9C876D]"
                      }`}
                    />

                    <div className="relative flex h-full flex-col justify-between p-10 text-white">

                      <div className="flex items-center justify-between">
                        <p className="text-[9px] font-bold uppercase tracking-[4px] text-white/75">
                          AI CONTENT OS
                        </p>

                        <span className="rounded-full border border-white/30 bg-black/10 px-4 py-2 text-[9px] font-bold">
                          01 / 06
                        </span>
                      </div>

                      <div className="max-w-[94%]">

                        <p className="mb-5 text-[9px] font-bold uppercase tracking-[4px] text-[#E2C9A5]">
                          INTELLIGENCE BRIEF
                        </p>

                        <h3
                          className="text-[47px] leading-[0.92]"
                          style={{
                            fontFamily:
                              "Instrument Serif",
                          }}
                        >
                          {shortenText(
                            slide.title,
                            95
                          )}
                        </h3>

                        <p className="mt-6 max-w-[90%] text-[13px] leading-5 text-white/80">
                          {shortenText(
                            slide.body,
                            150
                          )}
                        </p>
                      </div>

                      <div className="flex items-center justify-between border-t border-white/25 pt-5 text-[9px] text-white/60">
                        <span>
                          {shortenText(
                            source,
                            35
                          )}
                        </span>

                        <span>
                          Swipe →
                        </span>
                      </div>

                    </div>
                  </>
                )}

                {/* SLIDE 2 — DEVELOPMENT */}

                {index === 1 && (
                  <div className="flex h-full flex-col p-10">

                    <TopBar
                      number="02"
                    />

                    <div className="mt-12">
                      <p className="text-[9px] font-bold uppercase tracking-[4px] text-[#9A8167]">
                        WHAT HAPPENED
                      </p>

                      <h3
                        className="mt-4 text-[50px] leading-[0.92] text-[#171615]"
                        style={{
                          fontFamily:
                            "Instrument Serif",
                        }}
                      >
                        The development
                      </h3>
                    </div>

                    <div className="my-auto rounded-[26px] bg-[#E7DDD0] p-7">

                      <span
                        className="text-[64px] leading-none text-[#AF977A]"
                        style={{
                          fontFamily:
                            "Instrument Serif",
                        }}
                      >
                        01
                      </span>

                      <p className="mt-5 text-[18px] font-semibold leading-7 text-[#292622]">
                        {shortenText(
                          slide.body,
                          180
                        )}
                      </p>
                    </div>

                    <SlideFooter
                      source={source}
                    />
                  </div>
                )}

                {/* SLIDE 3 — WHY IT MATTERS */}

                {index === 2 && (
                  <div className="flex h-full flex-col bg-[#E3EAE4] p-10">

                    <TopBar
                      number="03"
                    />

                    <div className="my-auto">

                      <p className="text-[9px] font-bold uppercase tracking-[4px] text-[#66766A]">
                        WHY IT MATTERS
                      </p>

                      <h3
                        className="mt-5 max-w-[90%] text-[51px] leading-[0.92] text-[#18201B]"
                        style={{
                          fontFamily:
                            "Instrument Serif",
                        }}
                      >
                        The bigger picture
                      </h3>

                      <div className="mt-10 border-l-2 border-[#819184] pl-6">
                        <p className="max-w-[90%] text-[18px] font-semibold leading-7 text-[#334038]">
                          {shortenText(
                            slide.body,
                            190
                          )}
                        </p>
                      </div>

                    </div>

                    <SlideFooter
                      source={source}
                    />
                  </div>
                )}

                {/* SLIDE 4 — WATCH */}

                {index === 3 && (
                  <>
                    {imageUrl && (
                      <img
                        src={imageUrl}
                        alt=""
                        crossOrigin="anonymous"
                        className="absolute right-0 top-0 h-full w-[46%] object-cover"
                      />
                    )}

                    <div className="relative flex h-full flex-col p-10">

                      <TopBar
                        number="04"
                      />

                      <div className="my-auto w-[52%]">

                        <p className="text-[9px] font-bold uppercase tracking-[4px] text-[#9A8167]">
                          WHAT TO WATCH
                        </p>

                        <h3
                          className="mt-5 text-[48px] leading-[0.92] text-[#171615]"
                          style={{
                            fontFamily:
                              "Instrument Serif",
                          }}
                        >
                          The next signal
                        </h3>

                        <p className="mt-7 text-[15px] font-semibold leading-6 text-[#4C4640]">
                          {shortenText(
                            slide.body,
                            155
                          )}
                        </p>

                      </div>

                      <SlideFooter
                        source={source}
                        narrow
                      />
                    </div>
                  </>
                )}

                {/* SLIDE 5 — BUSINESS IMPACT */}

                {index === 4 && (
                  <div className="flex h-full flex-col bg-[#E8DED1] p-10">

                    <TopBar
                      number="05"
                    />

                    <div className="my-auto">

                      <p className="text-[9px] font-bold uppercase tracking-[4px] text-[#90785F]">
                        BUSINESS IMPACT
                      </p>

                      <h3
                        className="mt-5 text-[49px] leading-[0.92] text-[#191714]"
                        style={{
                          fontFamily:
                            "Instrument Serif",
                        }}
                      >
                        Where value
                        <br />
                        may emerge
                      </h3>

                      <div className="mt-9 rounded-[24px] bg-[#FFF9F0] p-7">
                        <p className="text-[17px] font-semibold leading-7 text-[#3A342E]">
                          {shortenText(
                            slide.body,
                            185
                          )}
                        </p>
                      </div>

                    </div>

                    <SlideFooter
                      source={source}
                    />
                  </div>
                )}

                {/* SLIDE 6 — TAKEAWAY */}

                {index === 5 && (
                  <div className="flex h-full flex-col bg-[#18201C] p-10 text-white">

                    <TopBar
                      number="06"
                      dark
                    />

                    <div className="my-auto">

                      <span
                        className="text-[76px] leading-none text-[#C7AE8D]"
                        style={{
                          fontFamily:
                            "Instrument Serif",
                        }}
                      >
                        ❝
                      </span>

                      <p className="mt-4 text-[9px] font-bold uppercase tracking-[4px] text-[#C7AE8D]">
                        THE TAKEAWAY
                      </p>

                      <h3
                        className="mt-5 max-w-[94%] text-[47px] leading-[0.94]"
                        style={{
                          fontFamily:
                            "Instrument Serif",
                        }}
                      >
                        The signal behind
                        the noise
                      </h3>

                      <p className="mt-7 max-w-[88%] text-[16px] leading-7 text-white/75">
                        {slide.body}
                      </p>

                    </div>

                    <div className="flex items-center justify-between border-t border-white/20 pt-5 text-[9px] text-white/55">
                      <span>
                        {shortenText(
                          source,
                          35
                        )}
                      </span>

                      <span className="uppercase tracking-[2px]">
                        AI Content OS
                      </span>
                    </div>

                  </div>
                )}

              </div>
            </div>

            <button
              onClick={() =>
                downloadSlide(index)
              }
              className="mx-auto mt-4 rounded-full border border-[#CFC5B6] bg-white px-5 py-2 text-xs font-semibold text-[#574F47] hover:bg-[#F3EEE5]"
            >
              Download Slide {index + 1} PNG
            </button>

          </div>
        ))}

      </div>
    </section>
  );
}

/* --------------------------------
   Reusable slide elements
-------------------------------- */

function TopBar({
  number,
  dark = false,
}: {
  number: string;
  dark?: boolean;
}) {
  return (
    <div className="flex shrink-0 items-center justify-between">

      <p
        className={`text-[9px] font-bold uppercase tracking-[4px] ${
          dark
            ? "text-white/55"
            : "text-[#766B60]"
        }`}
      >
        AI CONTENT OS
      </p>

      <span
        className={`rounded-full border px-4 py-2 text-[9px] font-bold ${
          dark
            ? "border-white/20 text-white/60"
            : "border-[#D3C8B8] text-[#766B60]"
        }`}
      >
        {number} / 06
      </span>

    </div>
  );
}

function SlideFooter({
  source,
  narrow = false,
}: {
  source: string;
  narrow?: boolean;
}) {
  return (
    <div
      className={`flex shrink-0 items-center justify-between border-t border-[#D1C7B8] pt-5 text-[9px] text-[#81766A] ${
        narrow ? "w-[52%]" : ""
      }`}
    >
      <span>
        {shortenText(
          source,
          32
        )}
      </span>

      <span className="uppercase tracking-[2px]">
        Intelligence
      </span>
    </div>
  );
}
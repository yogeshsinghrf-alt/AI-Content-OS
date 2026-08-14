"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

type CarouselSlide = {
  label?: string;
  title?: string;
  body?: string;
};

type CarouselDeckProps = {
  headline: string;
  subtitle?: string;
  slides?: CarouselSlide[];
  source?: string;
  imageUrl?: string;
  packageId?: string;
};

function shortenText(
  text: string,
  limit: number
) {
  if (!text) return "";

  return text.length > limit
    ? `${text
        .slice(0, limit)
        .trim()}…`
    : text;
}

export default function CarouselDeck({
  headline,
  subtitle = "",
  slides: generatedSlides = [],
  source = "AI Content OS",
  imageUrl,
  packageId,
}: CarouselDeckProps) {
  const slideRefs =
    useRef<
      (HTMLDivElement | null)[]
    >([]);

  const fallbackSlides = [
    {
      label: "01",
      title: headline,
      body:
        subtitle ||
        "A concise look at the development shaping today's technology landscape.",
    },
    {
      label: "02",
      title: "The development",
      body:
        "Understand the development shaping the market.",
    },
    {
      label: "03",
      title: "The bigger picture",
      body:
        "Evaluate why this matters for business and technology.",
    },
    {
      label: "04",
      title: "The next signal",
      body:
        "Watch adoption, execution and competitive response.",
    },
    {
      label: "05",
      title: "Where value may emerge",
      body:
        "Identify where measurable business value may emerge.",
    },
    {
      label: "06",
      title: "The takeaway",
      body:
        "Follow the technology, but focus on where it creates measurable business value.",
    },
  ];

  const slides =
    Array.isArray(generatedSlides) &&
    generatedSlides.length === 6
      ? generatedSlides.map(
          (slide, index) => ({
            label:
              slide.label ||
              `${index + 1}`.padStart(
                2,
                "0"
              ),
            title:
              slide.title ||
              fallbackSlides[index]
                .title,
            body:
              slide.body ||
              fallbackSlides[index]
                .body,
          })
        )
      : fallbackSlides;

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

      document.body.appendChild(
        link
      );
      link.click();
      document.body.removeChild(
        link
      );
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

  async function saveCarouselToPackage() {
    if (!packageId) {
      throw new Error(
        "Package ID is missing."
      );
    }

    const savedSlides = [];

    for (
      let index = 0;
      index < slides.length;
      index++
    ) {
      const dataUrl =
        await createSlidePng(index);

      const blobResponse =
        await fetch(dataUrl);

      const blob =
        await blobResponse.blob();

      const formData =
        new FormData();

      formData.append(
        "package_id",
        packageId
      );

      formData.append(
        "platform",
        "carousel"
      );

      formData.append(
        "file",
        blob,
        `carousel-slide-${index + 1}.png`
      );

      formData.append(
        "slide",
        String(index + 1)
      );

      const response = await fetch(
        `${API}/image/upload-asset`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const message =
          await response.text();

        throw new Error(
          `Carousel slide ${index + 1} save failed: ${response.status} ${message}`
        );
      }

      savedSlides.push(
        await response.json()
      );
    }

    return savedSlides;
  }

  return (
    <section className="rounded-[32px] border border-[#E2DBD0] bg-[#FFFDF9] p-7 shadow-sm lg:p-9">
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
            Dedicated story source: {source}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={
              downloadCarouselPdf
            }
            className="w-fit rounded-2xl bg-[#171615] px-5 py-3 text-sm font-semibold text-white hover:bg-[#302D29]"
          >
            Download Full Carousel PDF
          </button>

          <button
            onClick={async () => {
              try {
                await saveCarouselToPackage();
                alert(
                  "Carousel saved to package."
                );
              } catch (error) {
                console.error(
                  "Carousel save failed:",
                  error
                );

                alert(
                  "Could not save carousel."
                );
              }
            }}
            disabled={!packageId}
            className="w-fit rounded-2xl border border-[#171615] bg-white px-5 py-3 text-sm font-semibold text-[#171615] hover:bg-[#F3EEE5] disabled:cursor-not-allowed disabled:opacity-40"
          >
            Save to Package
          </button>
        </div>
      </div>

      <div className="grid gap-8 xl:grid-cols-2">
        {slides.map(
          (slide, index) => (
            <div
              key={`${slide.label}-${index}`}
              className="flex flex-col"
            >
              <div
                style={{
                  width: "540px",
                  height: "540px",
                }}
                className="mx-auto max-w-full"
              >
                <div
                  ref={(element) => {
                    slideRefs.current[
                      index
                    ] = element;
                  }}
                  style={{
                    width: "540px",
                    height: "540px",
                    margin: 0,
                    boxSizing:
                      "border-box",
                  }}
                  className="relative flex flex-col overflow-hidden bg-[#F7F1E7]"
                >
                  {index === 0 ? (
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
  className={`absolute inset-0 carousel-cover-bg ${
    imageUrl
      ? "bg-gradient-to-t from-black/85 via-black/30 to-black/15"
      : "bg-gradient-to-br from-[#17211C] via-[#344139] to-[#9C876D]"
  }`}
/>
                      <div className="relative flex h-full flex-col justify-between p-10 text-white">
                        <TopBar
                          number="01"
                          dark
                        />

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
                              slide.title ||
                                headline,
                              95
                            )}
                          </h3>

                          <p className="mt-6 max-w-[90%] text-[13px] leading-5 text-white/90">
                            {shortenText(
                              slide.body ||
                                subtitle,
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
                  ) : (
                    <div
                      className={`flex h-full flex-col p-10 ${
                        index === 2
                          ? "bg-[#E3EAE4]"
                          : index === 4
                          ? "bg-[#E8DED1]"
                          : index === 5
                          ? "carousel-dark-slide bg-[#18201C] text-white"
                          : "bg-[#F7F1E7]"
                      }`}
                    >
                      <TopBar
                        number={`${index + 1}`.padStart(
                          2,
                          "0"
                        )}
                        dark={index === 5}
                      />

                      <div className="my-auto">
                        <p
                          className={`text-[9px] font-bold uppercase tracking-[4px] ${
                            index === 5
                              ? "text-[#C7AE8D]"
                              : "text-[#927F68]"
                          }`}
                        >
                          {slide.label}
                        </p>

                        <h3
                          className="mt-5 text-[46px] leading-[0.94]"
                          style={{
                            fontFamily:
                              "Instrument Serif",
                          }}
                        >
                          {shortenText(
                            slide.title || "",
                            90
                          )}
                        </h3>

                        <div
                          className={`mt-8 rounded-[24px] p-7 ${
                            index === 5
                              ? "bg-white/10"
                              : "bg-white/55"
                          }`}
                        >
                          <p className="text-[16px] font-semibold leading-7">
                            {shortenText(
                              slide.body || "",
                              190
                            )}
                          </p>
                        </div>
                      </div>

                      <SlideFooter
                        source={source}
                        dark={index === 5}
                      />
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
                Download Slide{" "}
                {index + 1} PNG
              </button>
            </div>
          )
        )}
      </div>
    </section>
  );
}

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
            ? "text-white/75"
            : "text-[#766B60]"
        }`}
      >
        AI CONTENT OS
      </p>

      <span
        className={`rounded-full border px-4 py-2 text-[9px] font-bold ${
          dark
            ? "border-white/30 text-white/80"
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
  dark = false,
}: {
  source: string;
  dark?: boolean;
}) {
  return (
    <div
      className={`flex shrink-0 items-center justify-between border-t pt-5 text-[9px] ${
        dark
          ? "border-white/30 text-white/75"
          : "border-[#D1C7B8] text-[#81766A]"
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

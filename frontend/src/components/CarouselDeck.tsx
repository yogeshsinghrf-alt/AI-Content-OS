"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

type CarouselDeckProps = {
  headline: string;
  subtitle?: string;
  points?: string[];
  source?: string;

  linkedinImage?: string;
  instagramImage?: string;
  xImage?: string;
};

export default function CarouselDeck({
  headline,
  subtitle = "",
  points = [],
  source = "AI Content OS",

  linkedinImage,
  instagramImage,
  xImage,
}: CarouselDeckProps) {
  const slideRefs =
    useRef<(HTMLDivElement | null)[]>([]);

  const safePoints = points.length
    ? points
    : [
        "Understand the development",
        "Evaluate the business impact",
        "Watch what happens next",
        "Identify the opportunity",
      ];

  const slides = [
    {
      number: "01",
      eyebrow: "THE BRIEF",
      title: headline,
      body:
        subtitle ||
        "A concise look at the development shaping today's technology landscape.",
      image: linkedinImage,
      layout: "cover",
    },

    {
      number: "02",
      eyebrow: "WHAT HAPPENED",
      title: "The development",
      body:
        safePoints[0] ||
        subtitle ||
        "A significant development is changing the direction of the industry.",
      image: instagramImage,
      layout: "split",
    },

    {
      number: "03",
      eyebrow: "WHY IT MATTERS",
      title: "The bigger picture",
      body:
        safePoints[1] ||
        "The importance lies in how this changes business, technology and competitive strategy.",
      image: undefined,
      layout: "editorial",
    },

    {
      number: "04",
      eyebrow: "WHAT TO WATCH",
      title: "The next signal",
      body:
        safePoints[2] ||
        "Watch adoption, competitive response and real-world implementation.",
      image: xImage,
      layout: "image",
    },

    {
      number: "05",
      eyebrow: "BUSINESS IMPACT",
      title: "Where the opportunity is",
      body:
        safePoints[3] ||
        "Organizations that translate this development into practical workflows may gain an early advantage.",
      image: undefined,
      layout: "statement",
    },

    {
      number: "06",
      eyebrow: "THE TAKEAWAY",
      title: "Follow the signal, not the noise.",
      body:
        "Focus on where the development creates measurable business value and durable competitive advantage.",
      image: linkedinImage,
      layout: "closing",
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
      link.click();
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
        unit: "px",
        format: [1080, 1080],
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
            [1080, 1080],
            "portrait"
          );
        }

        pdf.addImage(
          dataUrl,
          "PNG",
          0,
          0,
          1080,
          1080
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

  async function printCarousel() {
    try {
      const images: string[] = [];

      for (
        let index = 0;
        index < slides.length;
        index++
      ) {
        images.push(
          await createSlidePng(index)
        );
      }

      const printWindow =
        window.open("", "_blank");

      if (!printWindow) {
        alert(
          "Please allow pop-ups for printing."
        );
        return;
      }

      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>AI Content OS Carousel</title>

            <style>
              body {
                margin: 0;
                background: white;
              }

              .slide {
                width: 100%;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                page-break-after: always;
              }

              img {
                width: 100%;
                max-width: 1080px;
                height: auto;
              }

              @page {
                margin: 0;
              }
            </style>
          </head>

          <body>
            ${images
              .map(
                (image) => `
                  <div class="slide">
                    <img src="${image}" />
                  </div>
                `
              )
              .join("")}

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
      console.error(
        "Carousel print failed:",
        error
      );

      alert(
        "Could not prepare carousel for printing."
      );
    }
  }

  return (
    <section className="mt-10">
      <div className="mb-6">
        <p className="text-xs font-bold uppercase tracking-[4px] text-[#9A8D7D]">
          Carousel Studio
        </p>

        <h2
          className="mt-2 text-4xl text-[#171615]"
          style={{
            fontFamily: "Instrument Serif",
          }}
        >
          6-slide editorial carousel
        </h2>

        <p className="mt-2 text-[#6F675E]">
          A visual editorial deck structured
          for LinkedIn and Instagram.
        </p>
      </div>

      <div className="mb-8 flex flex-wrap gap-3">
        <button
          onClick={downloadCarouselPdf}
          className="rounded-2xl bg-[#171615] px-5 py-3 font-semibold text-white hover:bg-[#302D29]"
        >
          Download Full Carousel PDF
        </button>

        <button
          onClick={printCarousel}
          className="rounded-2xl border border-[#171615] bg-white px-5 py-3 font-semibold text-[#171615] hover:bg-[#F2EEE6]"
        >
          Print Carousel
        </button>
      </div>

      <div className="grid gap-8 xl:grid-cols-2">
        {slides.map((slide, index) => (
          <div
            key={slide.number}
            className="rounded-[32px] border border-[#E1D9CD] bg-[#FFFDF8] p-4 shadow-sm"
          >
            {/* Actual square carousel artwork */}
            <div
              ref={(element) => {
                slideRefs.current[index] =
                  element;
              }}
              className="aspect-square overflow-hidden rounded-[26px] bg-[#F7F1E7]"
            >
              {slide.layout === "cover" ? (
                <CoverSlide
                  slide={slide}
                  source={source}
                  index={index}
                  total={slides.length}
                />
              ) : slide.layout === "split" ? (
                <SplitSlide
                  slide={slide}
                  source={source}
                  index={index}
                  total={slides.length}
                />
              ) : slide.layout ===
                "editorial" ? (
                <EditorialSlide
                  slide={slide}
                  source={source}
                  index={index}
                  total={slides.length}
                />
              ) : slide.layout === "image" ? (
                <ImageSlide
                  slide={slide}
                  source={source}
                  index={index}
                  total={slides.length}
                />
              ) : slide.layout ===
                "statement" ? (
                <StatementSlide
                  slide={slide}
                  source={source}
                  index={index}
                  total={slides.length}
                />
              ) : (
                <ClosingSlide
                  slide={slide}
                  source={source}
                  index={index}
                  total={slides.length}
                />
              )}
            </div>

            <button
              onClick={() =>
                downloadSlide(index)
              }
              className="mt-4 rounded-full border border-[#CFC5B6] bg-white px-4 py-2 text-xs font-semibold text-[#574F47] hover:bg-[#F3EEE5]"
            >
              Download Slide {index + 1} PNG
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}


/* -----------------------------------------
   Shared footer
----------------------------------------- */

function SlideFooter({
  source,
  index,
  total,
}: {
  source: string;
  index: number;
  total: number;
}) {
  return (
    <div className="flex items-center justify-between border-t border-black/10 pt-4 text-[11px] text-[#71685F]">
      <span>{source}</span>

      <span>
        {String(index + 1).padStart(
          2,
          "0"
        )}{" "}
        /{" "}
        {String(total).padStart(
          2,
          "0"
        )}
      </span>
    </div>
  );
}


/* -----------------------------------------
   Slide 1
----------------------------------------- */

function CoverSlide({
  slide,
  source,
  index,
  total,
}: any) {
  return (
    <div className="relative h-full">
      {slide.image && (
        <img
          src={slide.image}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
        />
      )}

      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-black/10" />

      <div className="relative flex h-full flex-col justify-between p-10 text-white">
        <div>
          <p className="text-xs font-bold uppercase tracking-[4px]">
            AI CONTENT OS
          </p>
        </div>

        <div>
          <p className="mb-4 text-xs font-bold uppercase tracking-[4px] text-white/70">
            {slide.eyebrow}
          </p>

          <h3
            className="max-w-[92%] text-5xl leading-[0.95]"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            {slide.title}
          </h3>

          <p className="mt-5 max-w-[85%] text-base leading-7 text-white/80">
            {slide.body}
          </p>
        </div>

        <SlideFooter
          source={source}
          index={index}
          total={total}
        />
      </div>
    </div>
  );
}


/* -----------------------------------------
   Slide 2
----------------------------------------- */

function SplitSlide({
  slide,
  source,
  index,
  total,
}: any) {
  return (
    <div className="flex h-full flex-col bg-[#F7F1E7] p-8">
      <div className="mb-5 flex h-[45%] overflow-hidden rounded-[22px] bg-[#DED8CD]">
        {slide.image ? (
          <img
            src={slide.image}
            alt=""
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-[#E6DDCF] to-[#C7D5CD]" />
        )}
      </div>

      <div className="flex flex-1 flex-col justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[4px] text-[#9A8167]">
            {slide.eyebrow}
          </p>

          <h3
            className="mt-3 text-4xl leading-none text-[#171615]"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            {slide.title}
          </h3>

          <p className="mt-4 text-base leading-7 text-[#655D54]">
            {slide.body}
          </p>
        </div>

        <SlideFooter
          source={source}
          index={index}
          total={total}
        />
      </div>
    </div>
  );
}


/* -----------------------------------------
   Slide 3
----------------------------------------- */

function EditorialSlide({
  slide,
  source,
  index,
  total,
}: any) {
  return (
    <div className="flex h-full flex-col justify-between bg-[#E9E2D5] p-10">
      <div className="flex justify-between">
        <p className="text-xs font-bold uppercase tracking-[4px] text-[#826F5D]">
          {slide.eyebrow}
        </p>

        <span className="text-6xl text-[#C4B39F]">
          03
        </span>
      </div>

      <div>
        <h3
          className="max-w-[90%] text-6xl leading-[0.9] text-[#171615]"
          style={{
            fontFamily:
              "Instrument Serif",
          }}
        >
          {slide.title}
        </h3>

        <div className="my-7 h-px w-20 bg-[#171615]" />

        <p className="max-w-[85%] text-xl leading-8 text-[#62594F]">
          {slide.body}
        </p>
      </div>

      <SlideFooter
        source={source}
        index={index}
        total={total}
      />
    </div>
  );
}


/* -----------------------------------------
   Slide 4
----------------------------------------- */

function ImageSlide({
  slide,
  source,
  index,
  total,
}: any) {
  return (
    <div className="relative h-full">
      {slide.image && (
        <img
          src={slide.image}
          alt=""
          className="absolute inset-0 h-full w-full object-cover"
        />
      )}

      <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/10 to-black/80" />

      <div className="relative flex h-full flex-col justify-between p-10 text-white">
        <p className="text-xs font-bold uppercase tracking-[4px]">
          {slide.eyebrow}
        </p>

        <div>
          <h3
            className="text-5xl leading-none"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            {slide.title}
          </h3>

          <p className="mt-5 max-w-[85%] text-lg leading-7 text-white/85">
            {slide.body}
          </p>
        </div>

        <SlideFooter
          source={source}
          index={index}
          total={total}
        />
      </div>
    </div>
  );
}


/* -----------------------------------------
   Slide 5
----------------------------------------- */

function StatementSlide({
  slide,
  source,
  index,
  total,
}: any) {
  return (
    <div className="flex h-full flex-col justify-between bg-[#DDE5DE] p-10">
      <p className="text-xs font-bold uppercase tracking-[4px] text-[#657269]">
        {slide.eyebrow}
      </p>

      <div>
        <span
          className="text-8xl leading-none text-[#AEBFB3]"
          style={{
            fontFamily:
              "Instrument Serif",
          }}
        >
          “
        </span>

        <h3
          className="-mt-5 max-w-[90%] text-5xl leading-[0.98] text-[#182019]"
          style={{
            fontFamily:
              "Instrument Serif",
          }}
        >
          {slide.title}
        </h3>

        <p className="mt-6 max-w-[85%] text-lg leading-8 text-[#526057]">
          {slide.body}
        </p>
      </div>

      <SlideFooter
        source={source}
        index={index}
        total={total}
      />
    </div>
  );
}


/* -----------------------------------------
   Slide 6
----------------------------------------- */

function ClosingSlide({
  slide,
  source,
  index,
  total,
}: any) {
  return (
    <div className="relative h-full bg-[#171615]">
      {slide.image && (
        <img
          src={slide.image}
          alt=""
          className="absolute right-0 top-0 h-full w-[48%] object-cover opacity-60"
        />
      )}

      <div className="absolute inset-0 bg-gradient-to-r from-[#171615] via-[#171615]/95 to-[#171615]/30" />

      <div className="relative flex h-full flex-col justify-between p-10 text-white">
        <p className="text-xs font-bold uppercase tracking-[4px] text-white/60">
          {slide.eyebrow}
        </p>

        <div className="max-w-[70%]">
          <h3
            className="text-6xl leading-[0.9]"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            {slide.title}
          </h3>

          <p className="mt-6 text-lg leading-8 text-white/70">
            {slide.body}
          </p>
        </div>

        <SlideFooter
          source={source}
          index={index}
          total={total}
        />
      </div>
    </div>
  );
}
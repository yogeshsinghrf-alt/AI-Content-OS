"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

type CarouselDeckProps = {
  headline: string;
  subtitle?: string;
  points?: string[];
  source?: string;
};

export default function CarouselDeck({
  headline,
  subtitle = "",
  points = [],
  source = "AI Content OS",
}: CarouselDeckProps) {
  const slideRefs = useRef<(HTMLDivElement | null)[]>([]);
  const safePoints = points.length
    ? points
    : [
        "Understand the development",
        "Evaluate the business impact",
        "Watch what happens next",
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
      body: safePoints[0] || subtitle,
    },

    {
      number: "03",
      eyebrow: "WHY IT MATTERS",
      title: "The bigger picture",
      body:
        safePoints[1] ||
        "The real importance lies in how this changes business, technology and competitive strategy.",
    },

    {
      number: "04",
      eyebrow: "KEY INSIGHT",
      title: "What to watch",
      body:
        safePoints[2] ||
        "Watch adoption, competitive response and real-world implementation.",
    },

    {
      number: "05",
      eyebrow: "BUSINESS IMPACT",
      title: "Where the opportunity is",
      body:
        safePoints[3] ||
        "Organizations that translate the development into practical workflows may gain an early advantage.",
    },

    {
      number: "06",
      eyebrow: "TAKEAWAY",
      title: "The signal behind the noise",
      body:
        "Follow the technology, but focus on where it creates measurable business value.",
    },
  ];
  async function createSlidePng(index: number) {
  const slide = slideRefs.current[index];

  if (!slide) {
    throw new Error("Carousel slide not found.");
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
    const dataUrl = await createSlidePng(index);

    const link = document.createElement("a");

    link.download =
      `carousel-slide-${index + 1}.png`;

    link.href = dataUrl;
    link.click();
  } catch (error) {
    console.error(
      "Carousel PNG export failed:",
      error
    );

    alert("Could not download this slide.");
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
        pdf.addPage([1080, 1080], "portrait");
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

    pdf.save("AI-Content-OS-carousel.pdf");
  } catch (error) {
    console.error(
      "Carousel PDF export failed:",
      error
    );

    alert("Could not download carousel PDF.");
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
        <p className="text-xs font-semibold uppercase tracking-[4px] text-[#8B8175]">
          Carousel Studio
        </p>

        <h2
          className="mt-2 text-4xl text-[#171615]"
          style={{ fontFamily: "Instrument Serif" }}
        >
          6-slide editorial carousel
        </h2>

        <p className="mt-2 text-[#6F675E]">
          Automatically structured for LinkedIn and Instagram.
        </p>
      </div>
      <div className="mb-6 flex flex-wrap gap-3">
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
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        {slides.map((slide, index) => (
  <div key={index}>

    {/* THIS is the actual 1080 × 1080 artwork */}
    <div
      ref={(element) => {
        slideRefs.current[index] = element;
      }}
      className="aspect-square overflow-hidden rounded-[30px] border border-[#DED7CB] bg-[#F7F1E7] shadow-sm"
    >
      <div className="flex h-full flex-col justify-between p-10">

        <div className="flex items-center justify-between">
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#766B60]">
            AI CONTENT OS
          </p>

          <span className="rounded-full border border-[#D3C8B8] bg-white/70 px-4 py-2 text-xs font-bold text-[#766B60]">
            {slide.number} / 06
          </span>
        </div>

        <div className="max-w-[90%]">
          <p className="mb-5 text-xs font-bold uppercase tracking-[4px] text-[#A08B70]">
            {slide.eyebrow}
          </p>

          <h3
            className="text-5xl leading-[0.96] text-[#171615]"
            style={{
              fontFamily: "Instrument Serif",
            }}
          >
            {slide.title}
          </h3>

          <p className="mt-6 text-lg leading-8 text-[#655D54]">
            {slide.body}
          </p>
        </div>

        <div className="flex items-center justify-between border-t border-[#D8CFC1] pt-5 text-xs text-[#81766A]">
          <span>{source}</span>

          <div className="flex gap-2">
            {slides.map((_, dotIndex) => (
              <span
                key={dotIndex}
                className={`h-2 rounded-full ${
                  dotIndex === index
                    ? "w-8 bg-[#171615]"
                    : "w-2 bg-[#CABFAF]"
                }`}
              />
            ))}
          </div>
        </div>

      </div>
    </div>

    <button
  onClick={() =>
    downloadSlide(index)
  }
  className="mt-4 w-fit rounded-full border border-[#CFC5B6] bg-white px-4 py-2 text-xs font-semibold text-[#574F47] hover:bg-[#F3EEE5]"
>
  Download Slide PNG
    </button>
    <button
      onClick={() => downloadSlide(index)}
      className="mt-3 rounded-full border border-[#CFC5B6] bg-white px-4 py-2 text-xs font-semibold text-[#574F47] hover:bg-[#F3EEE5]"
    >
      Download Slide {index + 1} PNG
    </button>

  </div>
))}
      </div>
    </section>
  );
}
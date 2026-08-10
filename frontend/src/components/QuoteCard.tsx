"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

type QuoteCardProps = {
  quote: string;
  source?: string;
};

function shortenText(
  text: string,
  limit: number
) {
  if (!text) return "";

  return text.length > limit
    ? `${text.slice(0, limit).trim()}…`
    : text;
}

export default function QuoteCard({
  quote,
  source = "AI Content OS",
}: QuoteCardProps) {
  const cardRef =
    useRef<HTMLDivElement | null>(null);

  async function createPng() {
    if (!cardRef.current) {
      throw new Error(
        "Quote card not found."
      );
    }

    return await toPng(
      cardRef.current,
      {
        cacheBust: true,
        pixelRatio: 2,
        backgroundColor: "#19201C",
      }
    );
  }

  async function downloadPng() {
    try {
      const dataUrl =
        await createPng();

      const link =
        document.createElement("a");

      link.download =
        "AI-Content-OS-quote-1080x1080.png";

      link.href = dataUrl;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

    } catch (error) {
      console.error(
        "Quote PNG failed:",
        error
      );

      alert(
        "Could not download quote PNG."
      );
    }
  }

  async function downloadPdf() {
    try {
      const dataUrl =
        await createPng();

      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: [216, 216],
      });

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

      pdf.save(
        "AI-Content-OS-quote.pdf"
      );

    } catch (error) {
      console.error(
        "Quote PDF failed:",
        error
      );

      alert(
        "Could not download quote PDF."
      );
    }
  }

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#8A7E70]">
            Visual Output
          </p>

          <h3 className="mt-1 text-2xl font-black text-[#171615]">
            Quote Card
          </h3>
        </div>

        <span className="rounded-full bg-[#F0ECE4] px-4 py-2 text-xs font-semibold text-[#6F675E]">
          1080 × 1080
        </span>
      </div>

      <div className="overflow-auto rounded-[24px] bg-[#EDE8DE] p-6">
        <div
          style={{
            width: "540px",
            height: "540px",
          }}
          className="mx-auto"
        >
          <div
            ref={cardRef}
            style={{
              width: "540px",
              height: "540px",
              minWidth: "540px",
              minHeight: "540px",
              maxWidth: "540px",
              maxHeight: "540px",
              margin: "0",
              boxSizing: "border-box",
            }}
            className="relative flex flex-col overflow-hidden bg-[#19201C] p-12 text-white"
          >
            <div className="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-[#58695F]/35" />

            <div className="absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-[#C8AE8A]/20" />

            <div className="relative flex shrink-0 items-center justify-between">
              <p className="text-[10px] font-bold uppercase tracking-[4px] text-white/60">
                AI CONTENT OS
              </p>

              <span
                className="text-[68px] leading-none text-[#D6C09F]"
                style={{
                  fontFamily:
                    "Instrument Serif",
                }}
              >
                ❝
              </span>
            </div>

            <div className="relative my-auto max-w-[94%]">
              <p className="mb-5 text-[10px] font-bold uppercase tracking-[4px] text-[#C9B28E]">
                INSIGHT / TODAY
              </p>

              <blockquote
                className="text-[38px] leading-[1.03]"
                style={{
                  fontFamily:
                    "Instrument Serif",
                }}
              >
                {shortenText(
                  quote,
                  190
                )}
              </blockquote>
            </div>

            <div className="relative flex shrink-0 items-center justify-between border-t border-white/20 pt-5 text-[9px] text-white/55">
              <span>
                {shortenText(
                  source,
                  42
                )}
              </span>

              <span className="uppercase tracking-[2px]">
                Perspective
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          onClick={downloadPng}
          className="rounded-2xl bg-[#171615] px-5 py-3 font-semibold text-white hover:bg-[#302D29]"
        >
          Download PNG
        </button>

        <button
          onClick={downloadPdf}
          className="rounded-2xl border border-[#171615] bg-white px-5 py-3 font-semibold text-[#171615] hover:bg-[#F2EEE6]"
        >
          Download PDF
        </button>
      </div>
    </div>
  );
}
"use client";

import { useRef } from "react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";
const API =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

type InfographicCardProps = {
  headline: string;
  subtitle?: string;
  points?: string[];
  source?: string;
  packageId?: string;
};

function shortenText(text: string, limit: number) {
  if (!text) return "";

  return text.length > limit
    ? `${text.slice(0, limit).trim()}…`
    : text;
}

export default function InfographicCard({
  headline,
  subtitle = "",
  points = [],
  source = "AI Content OS",
  packageId,
}: InfographicCardProps) {
  const cardRef = useRef<HTMLDivElement | null>(null);

  const fallbackPoints = [
    "Understand the key development.",
    "Evaluate why the development matters.",
    "Watch the next stage of adoption.",
    "Consider the business implications.",
  ];

  const safePoints = Array.from(
    { length: 4 },
    (_, index) =>
      points[index] ||
      fallbackPoints[index]
  );

  const labels = [
    "THE DEVELOPMENT",
    "WHY IT MATTERS",
    "WHAT TO WATCH",
    "BUSINESS IMPACT",
  ];

  async function createPng() {
  if (!cardRef.current) {
    throw new Error("Infographic not found.");
  }

  return await toPng(cardRef.current, {
    cacheBust: true,
    pixelRatio: 2,
    backgroundColor: "#F7F1E7",
  });
}
  async function saveToPackage() {
  if (!packageId) {
    throw new Error(
      "Package ID is missing."
    );
  }

  const dataUrl = await createPng();

  const blobResponse = await fetch(
    dataUrl
  );

  const blob = await blobResponse.blob();

  const formData = new FormData();

  formData.append(
    "package_id",
    packageId
  );

  formData.append(
    "platform",
    "infographic"
  );

  formData.append(
    "file",
    blob,
    "infographic.png"
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
      `Infographic save failed: ${response.status} ${message}`
    );
  }

  return await response.json();
}
  async function downloadPng() {
  try {
    const dataUrl = await createPng();

    const link = document.createElement("a");

    link.download =
      "AI-Content-OS-infographic-1080x1350.png";

    link.href = dataUrl;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error(
      "Infographic PNG export failed:",
      error
    );

    alert(
      "Could not download infographic PNG."
    );
  }
}

  async function downloadPdf() {
  try {
    const dataUrl = await createPng();

    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: [216, 270],
    });

    pdf.addImage(
      dataUrl,
      "PNG",
      0,
      0,
      216,
      270,
      undefined,
      "FAST"
    );

    pdf.save(
      "AI-Content-OS-infographic.pdf"
    );
  } catch (error) {
    console.error(
      "Infographic PDF export failed:",
      error
    );

    alert(
      "Could not download infographic PDF."
    );
  }
}

  return (
    <div>
      {/* Output header */}
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#8A7E70]">
            Visual Output
          </p>

          <h3 className="mt-1 text-2xl font-black text-[#171615]">
            Infographic
          </h3>
        </div>

        <span className="rounded-full bg-[#F0ECE4] px-4 py-2 text-xs font-semibold text-[#6F675E]">
          1080 × 1350
        </span>
      </div>

      {/* Preview area */}
      <div className="overflow-auto rounded-[24px] bg-[#EDE8DE] p-6">
        {/* 
          This is the actual artwork.

          540 × 675 is exactly a 40% preview
          of 1080 × 1350.
        */}
        <div
  style={{
    width: "540px",
    height: "675px",
  }}
  className="mx-auto"
>
  <div
    ref={cardRef}
    style={{
      width: "540px",
      height: "675px",
      minWidth: "540px",
      minHeight: "675px",
      maxWidth: "540px",
      maxHeight: "675px",
      margin: "0",
      paddingLeft: "40px",
      paddingRight: "40px",
      paddingTop: "36px",
      paddingBottom: "32px",
      boxSizing: "border-box",
    }}
    className="flex flex-col overflow-hidden bg-[#F7F1E7]"
  >
          {/* Top brand row */}
          <div className="flex shrink-0 items-center justify-between">
            <p className="text-[9px] font-bold uppercase tracking-[4px] text-[#766B60]">
              AI CONTENT OS
            </p>

            <span className="rounded-full border border-[#D2C7B8] px-3 py-1 text-[8px] font-bold uppercase tracking-[2px] text-[#766B60]">
              Intelligence Brief
            </span>
          </div>

          {/* Headline section */}
          <div className="mt-6 shrink-0">
            <p className="text-[9px] font-bold uppercase tracking-[4px] text-[#A08B70]">
              DATA STORY
            </p>

            <h2
              className="mt-2 max-w-[96%] text-[35px] leading-[0.94] text-[#171615]"
              style={{
                fontFamily:
                  "Instrument Serif",
              }}
            >
              {shortenText(headline, 78)}
            </h2>

            {subtitle && (
              <p className="mt-4 max-w-[96%] text-[12px] leading-[19px] text-[#6B6259]">
                {shortenText(
                  subtitle,
                  130
                )}
              </p>
            )}
          </div>

          {/* Insight grid */}
          <div className="mt-6 grid min-h-0 flex-1 grid-cols-2 grid-rows-2 gap-3">
            {safePoints.map(
              (point, index) => (
                <div
                  key={index}
                  className={`flex min-h-0 flex-col rounded-[18px] border p-4 ${
                    index === 0
                      ? "border-[#D4C5B1] bg-[#E9DED0]"
                      : index === 1
                      ? "border-[#CBD5CC] bg-[#E0E8E1]"
                      : index === 2
                      ? "border-[#D9D0C4] bg-[#FFFDF8]"
                      : "border-[#D4CEC2] bg-[#EEE9DF]"
                  }`}
                >
                  <span
                    className="shrink-0 text-[30px] leading-none text-[#B2A18C]"
                    style={{
                      fontFamily:
                        "Instrument Serif",
                    }}
                  >
                    0{index + 1}
                  </span>

                  <p className="mt-3 shrink-0 text-[8px] font-bold uppercase tracking-[2px] text-[#84776A]">
                    {labels[index]}
                  </p>

                  <p className="mt-4 text-[12px] font-semibold leading-[17px] text-[#302D29]">
                    {shortenText(
                      point,
                      95
                    )}
                  </p>
                </div>
              )
            )}
          </div>

          {/* Footer */}
<div className="mt-5 flex shrink-0 items-center justify-between border-t border-[#D5CCBE] pt-4 text-[8px] text-[#81766A]">
  <span>
    {shortenText(source, 40)}
  </span>

  <span className="font-bold uppercase tracking-[2px]">
    AI Content OS
  </span>
</div>

{/* Close actual infographic artwork */}
</div>

{/* Close centering wrapper */}
</div>

{/* Close preview area */}
</div>

{/* Export controls */}
<div className="mt-5 flex flex-wrap gap-3">
  <button
    onClick={downloadPng}
    className="rounded-2xl bg-[#171615] px-5 py-3 font-semibold text-white transition hover:bg-[#302D29]"
  >
    Download PNG
  </button>

  <button
    onClick={downloadPdf}
    className="rounded-2xl border border-[#171615] bg-white px-5 py-3 font-semibold text-[#171615] transition hover:bg-[#F2EEE6]"
  >
    Download PDF
  </button>
  <button
  onClick={async () => {
    try {
      const saved =
        await saveToPackage();

      console.log(
        "Infographic saved:",
        saved
      );

      alert(
        "Infographic saved to package."
      );
    } catch (error) {
      console.error(
        "Infographic save failed:",
        error
      );

      alert(
        "Could not save infographic."
      );
    }
  }}
  disabled={!packageId}
  className="rounded-2xl border border-[#171615] bg-white px-5 py-3 font-semibold text-[#171615] transition hover:bg-[#F2EEE6] disabled:cursor-not-allowed disabled:opacity-40"
>
  Save to Package
</button>
</div>

{/* Close component wrapper */}
</div>
);
}
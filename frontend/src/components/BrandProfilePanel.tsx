"use client";

export type BrandProfile = {
  enabled: boolean;
  companyName: string;
  audience: string;
  tone: string;
  cta: string;
  primaryColor: string;
  secondaryColor: string;
};

type Props = {
  value: BrandProfile;
  onChange: (value: BrandProfile) => void;
  onSave: () => void;
  onClear: () => void;
};

export default function BrandProfilePanel({
  value,
  onChange,
  onSave,
  onClear,
}: Props) {
  function updateField(
    field: keyof BrandProfile,
    fieldValue: string | boolean
  ) {
    onChange({
      ...value,
      [field]: fieldValue,
    });
  }

  const inputClass =
    "rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm text-[#3F3933] outline-none transition focus:border-[#A67C52] focus:ring-2 focus:ring-[#A67C52]/10";

  return (
    <section className="mt-6 rounded-[28px] border border-[#E3D8CA] bg-[#FFFDF8] p-6 shadow-sm">

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#A67C52]">
            BRAND PROFILE
          </p>

          <h2 className="mt-2 text-2xl font-semibold text-[#181716]">
            Generate content in your organisation&apos;s voice
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#70665D]">
            Optional. Apply audience, tone, CTA and brand palette
            while keeping every output grounded in its source.
          </p>
        </div>

        <label className="flex items-center gap-3 rounded-full border border-[#DED2C5] bg-white px-4 py-2.5 text-sm font-semibold text-[#5F574F]">
          <input
            type="checkbox"
            checked={value.enabled}
            onChange={(event) =>
              updateField(
                "enabled",
                event.target.checked
              )
            }
            className="h-4 w-4 accent-[#A67C52]"
          />

          Apply Brand Profile
        </label>

      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">

        <input
          value={value.companyName}
          onChange={(event) =>
            updateField(
              "companyName",
              event.target.value
            )
          }
          placeholder="Company name"
          className={inputClass}
        />

        <input
          value={value.audience}
          onChange={(event) =>
            updateField(
              "audience",
              event.target.value
            )
          }
          placeholder="Audience — e.g. technology executives"
          className={inputClass}
        />

        <input
          value={value.tone}
          onChange={(event) =>
            updateField(
              "tone",
              event.target.value
            )
          }
          placeholder="Tone — e.g. authoritative, concise, premium"
          className={inputClass}
        />

        <input
          value={value.cta}
          onChange={(event) =>
            updateField(
              "cta",
              event.target.value
            )
          }
          placeholder="Preferred CTA — e.g. Request a pilot"
          className={inputClass}
        />

        <input
          value={value.primaryColor}
          onChange={(event) =>
            updateField(
              "primaryColor",
              event.target.value
            )
          }
          placeholder="Primary colour — e.g. #A67C52"
          className={inputClass}
        />

        <input
          value={value.secondaryColor}
          onChange={(event) =>
            updateField(
              "secondaryColor",
              event.target.value
            )
          }
          placeholder="Secondary colour — e.g. #F7F3EB"
          className={inputClass}
        />

      </div>

      <div className="mt-5 flex flex-wrap gap-3">

        <button
          type="button"
          onClick={onSave}
          className="rounded-full border border-[#A67C52] bg-[#A67C52] px-5 py-2.5 text-sm font-semibold text-[#F7F3EB] shadow-sm transition hover:bg-[#956F49]"
        >
          Save Profile
        </button>

        <button
          type="button"
          onClick={onClear}
          className="rounded-full border border-[#D8D0C5] bg-white px-5 py-2.5 text-sm font-semibold text-[#5F574F] transition hover:border-[#A67C52]/60 hover:text-[#A67C52]"
        >
          Clear
        </button>

      </div>

    </section>
  );
}
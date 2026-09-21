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

  return (
    <section className="mt-6 mb-8 rounded-[28px] border border-[#E5DED3] bg-[#FFFDF8] p-6 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[3px] text-[#927F68]">
            BRAND PROFILE
          </p>

          <h2 className="mt-2 text-2xl font-semibold text-[#181716]">
            Generate content in your organisation&apos;s voice
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#70665D]">
            Optional. Apply audience, tone, CTA and brand palette
            while keeping every output grounded in its assigned source.
          </p>
        </div>

        <label className="flex items-center gap-3 text-sm font-semibold text-[#5F574F]">
          <input
            type="checkbox"
            checked={value.enabled}
            onChange={(event) =>
              updateField(
                "enabled",
                event.target.checked
              )
            }
            className="h-4 w-4"
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
          className="rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
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
          className="rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
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
          className="rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
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
          className="rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
        />

        <input
          value={value.primaryColor}
          onChange={(event) =>
            updateField(
              "primaryColor",
              event.target.value
            )
          }
          placeholder="Primary colour — e.g. #181716"
          className="rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
        />

        <input
          value={value.secondaryColor}
          onChange={(event) =>
            updateField(
              "secondaryColor",
              event.target.value
            )
          }
          placeholder="Secondary colour — e.g. #B08B5A"
          className="rounded-2xl border border-[#DED7CC] bg-white px-4 py-3 text-sm outline-none"
        />
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onSave}
          className="rounded-full bg-[#181716] px-5 py-2.5 text-sm font-semibold text-white"
        >
          Save Profile
        </button>

        <button
          type="button"
          onClick={onClear}
          className="rounded-full border border-[#D8D0C5] bg-white px-5 py-2.5 text-sm font-semibold text-[#5F574F]"
        >
          Clear
        </button>
      </div>
    </section>
  );
}
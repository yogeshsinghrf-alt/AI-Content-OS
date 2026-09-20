"use client";

import {
  FormEvent,
  useState,
} from "react";

export default function LoginPage() {
  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  async function handleSubmit(
    event: FormEvent,
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response =
        await fetch("/api/login", {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            password,
          }),
        });

      const result =
        await response.json();

      if (!response.ok) {
        setError(
          result?.detail ||
            "Login failed.",
        );

        return;
      }

      window.location.href = "/";
    } catch {
      setError(
        "Could not complete login.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#F5F2EA] px-6 py-12 text-[#181716]">
      <div className="mx-auto flex min-h-[80vh] max-w-md items-center">
        <div className="w-full rounded-[32px] border border-[#E3DDD3] bg-[#FFFDF8] p-8 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-[4px] text-[#8B8175]">
            ELANROVE
          </p>

          <h1
            className="mt-5 text-5xl"
            style={{
              fontFamily:
                "Instrument Serif",
            }}
          >
            AI Content OS
          </h1>

          <p className="mt-3 text-sm leading-6 text-[#70665D]">
            Protected demonstration environment.
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-8"
          >
            <label className="text-xs font-bold uppercase tracking-[2px] text-[#8B8175]">
              Access password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
              autoComplete="current-password"
              className="mt-3 w-full rounded-2xl border border-[#DDD5CA] bg-white px-5 py-4 outline-none focus:border-[#807161]"
              placeholder="Enter password"
              required
            />

            {error && (
              <p className="mt-4 text-sm text-red-700">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-6 w-full rounded-2xl bg-[#181716] px-5 py-4 font-semibold text-white disabled:opacity-50"
            >
              {loading
                ? "Checking…"
                : "Enter AI Content OS"}
            </button>
          </form>

          <p className="mt-6 text-xs leading-5 text-[#8B8175]">
            Authorized demo access only.
          </p>
        </div>
      </div>
    </main>
  );
}
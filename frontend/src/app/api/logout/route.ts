import { NextResponse } from "next/server";

export async function POST() {
  const response =
    NextResponse.json({
      authenticated: false,
    });

  response.cookies.set({
    name: "ai_content_os_session",
    value: "",
    httpOnly: true,
    secure:
      process.env.NODE_ENV ===
      "production",
    sameSite: "strict",
    path: "/",
    maxAge: 0,
  });

  return response;
}
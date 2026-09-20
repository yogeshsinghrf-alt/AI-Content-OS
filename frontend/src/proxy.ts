import {
  createHmac,
  timingSafeEqual,
} from "crypto";

import {
  NextRequest,
  NextResponse,
} from "next/server";

const SESSION_COOKIE =
  "ai_content_os_session";

function expectedSession(
  secret: string,
) {
  return createHmac("sha256", secret)
    .update("authenticated")
    .digest("hex");
}

function sessionIsValid(
  request: NextRequest,
) {
  const secret =
    process.env.APP_SESSION_SECRET;

  if (!secret) return false;

  const supplied =
    request.cookies.get(
      SESSION_COOKIE,
    )?.value;

  if (!supplied) return false;

  const expected =
    expectedSession(secret);

  const suppliedBuffer =
    Buffer.from(supplied);

  const expectedBuffer =
    Buffer.from(expected);

  return (
    suppliedBuffer.length ===
      expectedBuffer.length &&
    timingSafeEqual(
      suppliedBuffer,
      expectedBuffer,
    )
  );
}

export function proxy(
  request: NextRequest,
) {
  const pathname =
    request.nextUrl.pathname;

  if (
    pathname === "/login" ||
    pathname === "/api/login"
  ) {
    return NextResponse.next();
  }

  if (sessionIsValid(request)) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/api/")) {
    return NextResponse.json(
      {
        detail:
          "Authentication required.",
      },
      { status: 401 },
    );
  }

  return NextResponse.redirect(
    new URL("/login", request.url),
  );
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
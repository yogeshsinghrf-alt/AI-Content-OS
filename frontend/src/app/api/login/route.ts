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

const LOGIN_LIMIT = 5;
const LOGIN_WINDOW_MS = 10 * 60 * 1000;

const loginAttempts = new Map<
  string,
  number[]
>();

function signSession(secret: string) {
  return createHmac("sha256", secret)
    .update("authenticated")
    .digest("hex");
}

function getClientIdentity(
  request: NextRequest,
) {
  const forwardedFor =
    request.headers.get("x-forwarded-for");

  if (forwardedFor) {
    return forwardedFor
      .split(",")[0]
      .trim();
  }

  return "unknown";
}

function checkLoginRateLimit(
  request: NextRequest,
) {
  const now = Date.now();

  const identity =
    getClientIdentity(request);

  const existing =
    loginAttempts.get(identity) ?? [];

  const recent = existing.filter(
    (timestamp) =>
      now - timestamp <
      LOGIN_WINDOW_MS,
  );

  if (recent.length >= LOGIN_LIMIT) {
    const oldest = recent[0];

    const retryAfterSeconds =
      Math.max(
        1,
        Math.ceil(
          (
            LOGIN_WINDOW_MS -
            (now - oldest)
          ) / 1000,
        ),
      );

    loginAttempts.set(
      identity,
      recent,
    );

    return retryAfterSeconds;
  }

  recent.push(now);

  loginAttempts.set(
    identity,
    recent,
  );

  return null;
}

export async function POST(
  request: NextRequest,
) {
  const retryAfter =
    checkLoginRateLimit(request);

  if (retryAfter !== null) {
    return NextResponse.json(
      {
        detail:
          "Too many login attempts. Try again later.",
      },
      {
        status: 429,
        headers: {
          "Retry-After":
            String(retryAfter),
        },
      },
    );
  }

  const appPassword =
    process.env.APP_ACCESS_PASSWORD;

  const sessionSecret =
    process.env.APP_SESSION_SECRET;

  if (!appPassword || !sessionSecret) {
    return NextResponse.json(
      {
        detail:
          "Application authentication is not configured.",
      },
      { status: 500 },
    );
  }

  const body = await request.json();

  const suppliedPassword =
    typeof body.password === "string"
      ? body.password
      : "";

  const supplied =
    Buffer.from(suppliedPassword);

  const expected =
    Buffer.from(appPassword);

  const passwordMatches =
    supplied.length === expected.length &&
    timingSafeEqual(
      supplied,
      expected,
    );

  if (!passwordMatches) {
    return NextResponse.json(
      {
        detail: "Invalid password.",
      },
      { status: 401 },
    );
  }

  const response =
    NextResponse.json({
      authenticated: true,
    });

  response.cookies.set({
    name: SESSION_COOKIE,
    value:
      signSession(sessionSecret),
    httpOnly: true,
    secure:
      process.env.NODE_ENV ===
      "production",
    sameSite: "strict",
    path: "/",
    maxAge: 60 * 60 * 8,
  });

  return response;
}
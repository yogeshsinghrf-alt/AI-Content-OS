import {
  NextRequest,
  NextResponse,
} from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

async function forwardRequest(
  request: NextRequest,
  context: RouteContext,
) {
  const backendUrl =
    process.env.BACKEND_API_URL;

  const backendApiKey =
    process.env.BACKEND_API_KEY;

  if (
    !backendUrl ||
    !backendApiKey
  ) {
    return NextResponse.json(
      {
        detail:
          "Backend connection is not configured.",
      },
      {
        status: 500,
      },
    );
  }

  const { path } =
    await context.params;

  const cleanBase =
    backendUrl.replace(/\/+$/, "");

  const targetPath =
    path
      .map((segment) =>
        encodeURIComponent(segment)
      )
      .join("/");

  const targetUrl =
    `${cleanBase}/${targetPath}` +
    request.nextUrl.search;

  const headers =
    new Headers();

  headers.set(
    "x-api-key",
    backendApiKey,
  );

  const contentType =
    request.headers.get(
      "content-type",
    );

  if (contentType) {
    headers.set(
      "content-type",
      contentType,
    );
  }

  const accept =
    request.headers.get("accept");

  if (accept) {
    headers.set(
      "accept",
      accept,
    );
  }

  const method =
    request.method;

  let body:
    | ArrayBuffer
    | undefined;

  if (
    method !== "GET" &&
    method !== "HEAD"
  ) {
    body =
      await request.arrayBuffer();
  }

  try {
    const backendResponse =
      await fetch(
        targetUrl,
        {
          method,
          headers,
          body,
          cache: "no-store",
          redirect: "manual",
        },
      );

    const responseHeaders =
      new Headers();

    const passThroughHeaders = [
      "content-type",
      "content-disposition",
      "cache-control",
      "retry-after",
    ];

    for (
      const headerName
      of passThroughHeaders
    ) {
      const value =
        backendResponse.headers.get(
          headerName,
        );

      if (value) {
        responseHeaders.set(
          headerName,
          value,
        );
      }
    }

    const noBody =
      backendResponse.status === 204 ||
      backendResponse.status === 304;

    const responseBody =
      noBody
        ? null
        : await backendResponse.arrayBuffer();

    return new NextResponse(
      responseBody,
      {
        status:
          backendResponse.status,
        headers:
          responseHeaders,
      },
    );
  } catch (error) {
    console.error(
      "Backend proxy failed:",
      error,
    );

    return NextResponse.json(
      {
        detail:
          "The backend service is temporarily unavailable.",
      },
      {
        status: 502,
      },
    );
  }
}

export async function GET(
  request: NextRequest,
  context: RouteContext,
) {
  return forwardRequest(
    request,
    context,
  );
}

export async function POST(
  request: NextRequest,
  context: RouteContext,
) {
  return forwardRequest(
    request,
    context,
  );
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext,
) {
  return forwardRequest(
    request,
    context,
  );
}

export async function PUT(
  request: NextRequest,
  context: RouteContext,
) {
  return forwardRequest(
    request,
    context,
  );
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext,
) {
  return forwardRequest(
    request,
    context,
  );
}
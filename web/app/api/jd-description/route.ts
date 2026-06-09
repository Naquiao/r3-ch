import { NextRequest, NextResponse } from "next/server";

import { normalizeAts } from "@/lib/opportunity-key";
import { masterPathForAts } from "@/lib/paths";
import { updateMasterOpportunityDescription } from "@/lib/storage";
import type { AtsProvider } from "@/lib/types";

type DescriptionPayload = {
  ats?: AtsProvider;
  slug?: string;
  job_id?: string | number;
  absolute_url?: string;
  existing_description?: string | null;
};

export const runtime = "nodejs";

function stripHtml(value: string): string {
  return value
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function pickDescriptionFromHtml(html: string): string {
  const og = html.match(/<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']+)["']/i);
  if (og?.[1]) return og[1].trim();

  const meta = html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["']/i);
  if (meta?.[1]) return meta[1].trim();

  const main = html.match(/<main[\s\S]*?<\/main>/i)?.[0] ?? html.match(/<body[\s\S]*?<\/body>/i)?.[0] ?? html;
  const cleaned = stripHtml(main);
  return cleaned.slice(0, 2000);
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  let payload: DescriptionPayload;
  try {
    payload = (await request.json()) as DescriptionPayload;
  } catch {
    return NextResponse.json({ error: "Invalid JSON payload." }, { status: 400 });
  }

  const slug = `${payload.slug ?? ""}`.trim();
  const jobId = `${payload.job_id ?? ""}`.trim();
  const absoluteUrl = `${payload.absolute_url ?? ""}`.trim();
  const existingDescription = `${payload.existing_description ?? ""}`.trim();

  if (!slug || !jobId || !absoluteUrl) {
    return NextResponse.json({ error: "slug, job_id and absolute_url are required." }, { status: 400 });
  }

  if (existingDescription) {
    return NextResponse.json({ source: "existing", description: existingDescription });
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(absoluteUrl);
  } catch {
    return NextResponse.json({ error: "absolute_url is not a valid URL." }, { status: 400 });
  }

  if (parsedUrl.protocol !== "http:" && parsedUrl.protocol !== "https:") {
    return NextResponse.json({ error: "Only http/https URLs are supported." }, { status: 400 });
  }

  try {
    const response = await fetch(parsedUrl.toString(), {
      method: "GET",
      signal: AbortSignal.timeout(10_000),
      headers: {
        "user-agent": "r3-ch-opportunity-review/1.0",
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `Failed to fetch JD page (${response.status}).` },
        { status: 502 },
      );
    }

    const html = await response.text();
    const description = pickDescriptionFromHtml(html);
    
    let persisted = false;
    if (description) {
      const ats = normalizeAts(payload.ats);
      const masterPath = masterPathForAts(ats);
      persisted = await updateMasterOpportunityDescription(masterPath, slug, jobId, description);
    }

    return NextResponse.json({ source: "fetched", description, persisted });
  } catch (error) {
    return NextResponse.json(
      { error: `Could not fetch JD description: ${String(error)}` },
      { status: 502 },
    );
  }
}

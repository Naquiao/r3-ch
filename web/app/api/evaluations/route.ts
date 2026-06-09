import { NextRequest, NextResponse } from "next/server";

import { buildOpportunityKey, normalizeAts } from "@/lib/opportunity-key";
import { EVALUATIONS_PATH } from "@/lib/paths";
import { readEvaluations, writeEvaluationsAtomic } from "@/lib/storage";
import type { AtsProvider, Decision } from "@/lib/types";

export const runtime = "nodejs";

type EvaluationPayload = {
  ats?: AtsProvider;
  slug?: string;
  job_id?: string | number;
  decision?: Decision;
  notes?: string;
};

type BulkEvaluationPayload = {
  items?: EvaluationPayload[];
};

function isDecision(value: string): value is Decision {
  return value === "interested" || value === "not_interested" || value === "later";
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  let payload: EvaluationPayload | BulkEvaluationPayload;
  try {
    payload = (await request.json()) as EvaluationPayload | BulkEvaluationPayload;
  } catch {
    return NextResponse.json({ error: "Invalid JSON payload." }, { status: 400 });
  }

  const updates = Array.isArray((payload as BulkEvaluationPayload).items)
    ? (payload as BulkEvaluationPayload).items ?? []
    : [payload as EvaluationPayload];

  if (updates.length === 0) {
    return NextResponse.json(
      { error: "At least one evaluation update is required." },
      { status: 400 },
    );
  }

  const evaluations = await readEvaluations(EVALUATIONS_PATH);
  const updatedKeys: string[] = [];
  const now = new Date().toISOString();

  for (const update of updates) {
    const slug = `${update.slug ?? ""}`.trim();
    const jobId = `${update.job_id ?? ""}`.trim();
    const decision = `${update.decision ?? ""}`.trim();
    const notes = `${update.notes ?? ""}`.trim();
    const ats = normalizeAts(update.ats);

    if (!slug || !jobId || !isDecision(decision)) {
      return NextResponse.json(
        { error: "Every item requires slug, job_id and a valid decision." },
        { status: 400 },
      );
    }

    const key = buildOpportunityKey(ats, slug, jobId);
    evaluations[key] = {
      decision,
      notes: notes || undefined,
      updated_at: now,
    };
    updatedKeys.push(key);
  }

  await writeEvaluationsAtomic(EVALUATIONS_PATH, evaluations);

  if (updatedKeys.length === 1) {
    const [key] = updatedKeys;
    return NextResponse.json({ ok: true, key, evaluation: evaluations[key] });
  }

  return NextResponse.json({
    ok: true,
    count: updatedKeys.length,
    keys: updatedKeys,
  });
}

import { NextRequest, NextResponse } from "next/server";

import { buildOpportunityKey, normalizeAts } from "@/lib/opportunity-key";
import { EVALUATIONS_PATH } from "@/lib/paths";
import { readEvaluations, writeEvaluationsAtomic } from "@/lib/storage";
import type { AtsProvider, Decision, FunnelStage } from "@/lib/types";

export const runtime = "nodejs";

type EvaluationPayload = {
  ats?: AtsProvider;
  slug?: string;
  job_id?: string | number;
  decision?: Decision;
  stage?: FunnelStage;
  notes?: string;
};

type BulkEvaluationPayload = {
  items?: EvaluationPayload[];
};

function isDecision(value: string): value is Decision {
  return value === "interested" || value === "not_interested" || value === "later";
}

function isStage(value: string): value is FunnelStage {
  return value === "stage_0"
    || value === "applied"
    || value === "in_progress"
    || value === "won"
    || value === "lost";
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
    const stageRaw = update.stage ? `${update.stage}`.trim() : "";
    const notes = `${update.notes ?? ""}`.trim();
    const ats = normalizeAts(update.ats);

    if (!slug || !jobId || !isDecision(decision)) {
      return NextResponse.json(
        { error: "Every item requires slug, job_id and a valid decision." },
        { status: 400 },
      );
    }

    if (stageRaw && !isStage(stageRaw)) {
      return NextResponse.json(
        { error: "Stage is invalid. Allowed values: stage_0, applied, in_progress, won, lost." },
        { status: 400 },
      );
    }

    const key = buildOpportunityKey(ats, slug, jobId);
    const previous = evaluations[key];
    const incomingStage = isStage(stageRaw) ? stageRaw : undefined;
    const nextStage = decision === "interested"
      ? (incomingStage ?? previous?.stage ?? "stage_0")
      : undefined;

    evaluations[key] = {
      decision,
      stage: nextStage,
      notes: notes || previous?.notes,
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

import { NextRequest, NextResponse } from "next/server";

import {
  buildLegacyOpportunityKey,
  buildOpportunityKey,
  getAtsForOpportunity,
} from "@/lib/opportunity-key";
import {
  extractLocationTags,
  matchesLocationFilter,
  normalizeLocationFilter,
} from "@/lib/location";
import { EVALUATIONS_PATH, MASTER_MATCHES_PATHS } from "@/lib/paths";
import { readEvaluations, readMasterMatchesMany } from "@/lib/storage";
import type {
  AtsFilter,
  DecisionFilter,
  OpportunitySort,
  OpportunityWithEvaluation,
} from "@/lib/types";

export const runtime = "nodejs";

function parseSort(rawSort: string | null): OpportunitySort {
  return rawSort === "oldest" ? "oldest" : "newest";
}

function parseAtsFilter(rawAts: string | null): AtsFilter {
  if (rawAts === "greenhouse" || rawAts === "ashby" || rawAts === "lever" || rawAts === "bamboohr") return rawAts;
  return "all";
}

function getTimestamp(dateValue: string | null | undefined): number | null {
  if (!dateValue) return null;
  const timestamp = Date.parse(dateValue);
  if (Number.isNaN(timestamp)) return null;
  return timestamp;
}

function compareByUpdatedAt(
  a: OpportunityWithEvaluation,
  b: OpportunityWithEvaluation,
  sort: OpportunitySort,
): number {
  const aTimestamp = getTimestamp(a.updated_at);
  const bTimestamp = getTimestamp(b.updated_at);

  if (aTimestamp === null && bTimestamp === null) return 0;
  if (aTimestamp === null) return 1;
  if (bTimestamp === null) return -1;

  return sort === "oldest" ? aTimestamp - bTimestamp : bTimestamp - aTimestamp;
}

export async function GET(request: NextRequest): Promise<NextResponse> {
  const searchParams = request.nextUrl.searchParams;
  const location = normalizeLocationFilter(searchParams.get("location") ?? undefined);
  const decision = (searchParams.get("decision") ?? "all") as DecisionFilter;
  const sort = parseSort(searchParams.get("sort"));
  const ats = parseAtsFilter(searchParams.get("ats"));

  const [master, evaluations] = await Promise.all([
    readMasterMatchesMany(MASTER_MATCHES_PATHS),
    readEvaluations(EVALUATIONS_PATH),
  ]);

  const eligibleOnly = master.filter((record) => record.eligibility === "ok");
  const merged: OpportunityWithEvaluation[] = eligibleOnly.map((record) => {
    const recordAts = getAtsForOpportunity(record);
    const key = buildOpportunityKey(recordAts, record.slug, record.job_id);
    const legacyKey = buildLegacyOpportunityKey(record.slug, record.job_id);
    const evaluation = evaluations[key] ?? evaluations[legacyKey];
    return {
      ...record,
      ats: recordAts,
      key,
      decision: evaluation?.decision ?? null,
    };
  });

  const filtered = merged.filter((item) => {
    const locationMatches = matchesLocationFilter(item.location_raw, location);

    const decisionMatches = decision === "all"
      || (decision === "unclassified" && item.decision === null)
      || item.decision === decision;

    const atsMatches = ats === "all" || item.ats === ats;

    return locationMatches && decisionMatches && atsMatches;
  });

  filtered.sort((a, b) => compareByUpdatedAt(a, b, sort));

  const availableLocationTags = Array.from(
    new Set(
      merged.flatMap((item) => Array.from(extractLocationTags(item.location_raw))),
    ),
  ).sort();
  const availableAts = Array.from(new Set(merged.map((item) => item.ats))).sort();

  return NextResponse.json({
    items: filtered,
    total: filtered.length,
    meta: {
      source_total_eligible: merged.length,
      available_location_tags: availableLocationTags,
      available_ats: availableAts,
    },
  });
}

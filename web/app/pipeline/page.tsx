"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import type { FunnelStage, OpportunityWithEvaluation } from "@/lib/types";

type OpportunitiesResponse = {
  items: OpportunityWithEvaluation[];
  total: number;
  meta: {
    source_total_eligible: number;
    available_location_tags: string[];
    available_ats: string[];
  };
};

type StageColumn = {
  key: FunnelStage;
  title: string;
  description: string;
};

const STAGE_COLUMNS: StageColumn[] = [
  { key: "stage_0", title: "Stage 0", description: "Ready to apply" },
  { key: "applied", title: "Applied", description: "Application submitted" },
  { key: "in_progress", title: "In Progress", description: "Interviews and loops" },
  { key: "won", title: "Won", description: "Offer accepted" },
  { key: "lost", title: "Lost", description: "Rejected or withdrawn" },
];

function normalizeStage(item: OpportunityWithEvaluation): FunnelStage {
  return item.stage ?? "stage_0";
}

export default function PipelinePage(): ReactElement {
  const [items, setItems] = useState<OpportunityWithEvaluation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draggingKey, setDraggingKey] = useState<string | null>(null);

  async function loadPipeline(): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        decision: "interested",
        sort: "newest",
      });
      const response = await fetch(`/api/opportunities?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Could not load pipeline (${response.status})`);
      }
      const payload = (await response.json()) as OpportunitiesResponse;
      setItems(payload.items);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadPipeline();
  }, []);

  const grouped = useMemo(() => {
    const base: Record<FunnelStage, OpportunityWithEvaluation[]> = {
      stage_0: [],
      applied: [],
      in_progress: [],
      won: [],
      lost: [],
    };
    for (const item of items) {
      base[normalizeStage(item)].push(item);
    }
    return base;
  }, [items]);

  async function moveStage(item: OpportunityWithEvaluation, nextStage: FunnelStage): Promise<void> {
    if (normalizeStage(item) === nextStage) return;

    const response = await fetch("/api/evaluations", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        slug: item.slug,
        job_id: item.job_id,
        ats: item.ats,
        decision: "interested",
        stage: nextStage,
      }),
    });

    if (!response.ok) {
      setError(`Could not update stage (${response.status})`);
      return;
    }

    setItems((prev) =>
      prev.map((row) => (row.key === item.key ? { ...row, decision: "interested", stage: nextStage } : row)),
    );
  }

  async function handleDrop(stage: FunnelStage): Promise<void> {
    if (!draggingKey) return;
    const item = items.find((candidate) => candidate.key === draggingKey);
    setDraggingKey(null);
    if (!item) return;
    await moveStage(item, stage);
  }

  return (
    <>
      <header className="page-header">
        <span className="eyebrow">PIPELINE MANAGEMENT</span>
        <h1 className="h1">Bottom Funnel</h1>
        <p className="muted-text">Move interested roles from stage 0 through applied, in progress, won or lost.</p>
      </header>

      <div className="summary-pills">
        <span className="mono-label">Interested roles: {items.length}</span>
        <button className="btn-ghost" onClick={() => void loadPipeline()}>
          Refresh
        </button>
      </div>

      {loading && <div className="description-loading">Loading pipeline...</div>}
      {error && <div className="description-error">{error}</div>}

      {!loading && !error && items.length === 0 && (
        <div className="empty-state">NO INTERESTED ROLES YET</div>
      )}

      <section className="kanban-board" aria-label="Application pipeline">
        {STAGE_COLUMNS.map((column) => (
          <div
            key={column.key}
            className={`kanban-column ${draggingKey ? "is-drop-active" : ""}`}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              void handleDrop(column.key);
            }}
          >
            <header className="kanban-column-header">
              <h2 className="h3">{column.title}</h2>
              <span className="tag">{grouped[column.key].length}</span>
            </header>
            <p className="muted-text kanban-column-description">{column.description}</p>

            <div className="kanban-card-list">
              {grouped[column.key].length === 0 ? (
                <div className="kanban-empty">Drop opportunities here</div>
              ) : (
                grouped[column.key].map((item) => (
                  <article
                    key={item.key}
                    className="kanban-card"
                    draggable
                    onDragStart={() => setDraggingKey(item.key)}
                    onDragEnd={() => setDraggingKey(null)}
                  >
                    <h3 className="kanban-card-title">{item.title}</h3>
                    <p className="mono-label muted-text">
                      {item.slug} · {item.ats.toUpperCase()}
                    </p>
                    <p className="kanban-card-location">{item.location_raw ?? "Unknown location"}</p>
                    <div className="kanban-card-actions">
                      {item.absolute_url && (
                        <a href={item.absolute_url} className="btn-ghost" target="_blank" rel="noreferrer">
                          Open role
                        </a>
                      )}
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>
        ))}
      </section>
    </>
  );
}

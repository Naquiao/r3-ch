"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

import type {
  AtsFilter,
  Decision,
  DecisionFilter,
  OpportunitySort,
  OpportunityWithEvaluation,
} from "@/lib/types";

type OpportunitiesResponse = {
  items: OpportunityWithEvaluation[];
  total: number;
  meta: {
    source_total_eligible: number;
    available_location_tags: string[];
    available_ats: string[];
  };
};

type DescriptionState = {
  loading: boolean;
  text: string | null;
  error: string | null;
};

const DECISION_LABELS: Record<Decision, string> = {
  interested: "Interested",
  not_interested: "Pass",
  later: "Later",
};

const relativeTimeFormatter = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

function parseDate(value: string | null | undefined): Date | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function getOrdinalDay(day: number): string {
  const mod10 = day % 10;
  const mod100 = day % 100;
  if (mod10 === 1 && mod100 !== 11) return `${day}st`;
  if (mod10 === 2 && mod100 !== 12) return `${day}nd`;
  if (mod10 === 3 && mod100 !== 13) return `${day}rd`;
  return `${day}th`;
}

function formatFullDate(date: Date): string {
  const day = getOrdinalDay(date.getDate());
  const month = date.toLocaleString("en", { month: "long" });
  const year = date.getFullYear();
  return `${day} ${month}, ${year}`;
}

function formatRelativeTime(date: Date): string {
  const diffMs = date.getTime() - Date.now();
  const diffSec = Math.round(diffMs / 1000);
  const absSec = Math.abs(diffSec);

  if (absSec < 60) return relativeTimeFormatter.format(diffSec, "second");
  const diffMin = Math.round(diffSec / 60);
  if (Math.abs(diffMin) < 60) return relativeTimeFormatter.format(diffMin, "minute");
  const diffHour = Math.round(diffSec / 3600);
  if (Math.abs(diffHour) < 24) return relativeTimeFormatter.format(diffHour, "hour");
  const diffDay = Math.round(diffSec / 86400);
  if (Math.abs(diffDay) < 30) return relativeTimeFormatter.format(diffDay, "day");
  const diffMonth = Math.round(diffSec / 2_592_000);
  if (Math.abs(diffMonth) < 12) return relativeTimeFormatter.format(diffMonth, "month");
  const diffYear = Math.round(diffSec / 31_536_000);
  return relativeTimeFormatter.format(diffYear, "year");
}

function formatUpdatedAt(value: string | null | undefined): { relative: string; tooltip: string } {
  const parsed = parseDate(value);
  if (!parsed) {
    return { relative: "unknown", tooltip: "Unknown date" };
  }
  return {
    relative: formatRelativeTime(parsed),
    tooltip: formatFullDate(parsed),
  };
}

function formatLocationTagLabel(tag: string): string {
  return tag.replaceAll("_", " ");
}

export default function HomePage(): ReactElement {
  const [items, setItems] = useState<OpportunityWithEvaluation[]>([]);
  const [locationFilter, setLocationFilter] = useState("");
  const [decisionFilter, setDecisionFilter] = useState<DecisionFilter>("unclassified");
  const [atsFilter, setAtsFilter] = useState<AtsFilter>("all");
  const [sortOrder, setSortOrder] = useState<OpportunitySort>("newest");
  const [locationTags, setLocationTags] = useState<string[]>([]);
  const [atsOptions, setAtsOptions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [descriptions, setDescriptions] = useState<Record<string, DescriptionState>>({});
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({});
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());

  function toggleCard(key: string) {
    setExpandedCards((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  async function loadData(
    nextLocation: string,
    nextDecision: DecisionFilter,
    nextAts: AtsFilter,
    nextSort: OpportunitySort,
  ): Promise<void> {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (nextLocation.trim()) params.set("location", nextLocation.trim());
      params.set("decision", nextDecision);
      params.set("ats", nextAts);
      params.set("sort", nextSort);
      const response = await fetch(`/api/opportunities?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Could not load opportunities (${response.status})`);
      }
      const payload = (await response.json()) as OpportunitiesResponse;
      setItems(payload.items);
      setLocationTags(payload.meta.available_location_tags);
      setAtsOptions(payload.meta.available_ats);
      setSelectedKeys(new Set());
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData(locationFilter, decisionFilter, atsFilter, sortOrder);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const summary = useMemo(() => {
    const totals: Record<string, number> = {
      interested: 0,
      not_interested: 0,
      later: 0,
      unclassified: 0,
    };
    for (const item of items) {
      if (!item.decision) totals.unclassified += 1;
      else totals[item.decision] += 1;
    }
    return totals;
  }, [items]);

  async function setDecision(item: OpportunityWithEvaluation, decision: Decision): Promise<void> {
    const response = await fetch("/api/evaluations", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        slug: item.slug,
        job_id: item.job_id,
        ats: item.ats,
        decision,
      }),
    });
    if (!response.ok) {
      setError(`Could not save decision (${response.status})`);
      return;
    }
    setItems((prev) =>
      prev
        .map((row) => (row.key === item.key ? { ...row, decision } : row))
        // Auto-hide the item if the new decision no longer matches the current filter
        .filter((row) => {
          if (decisionFilter === "all") return true;
          if (decisionFilter === "unclassified" && row.decision === null) return true;
          if (decisionFilter === row.decision) return true;
          return false;
        })
    );
    setSelectedKeys((prev) => {
      const next = new Set(prev);
      next.delete(item.key);
      return next;
    });
  }

  async function setDecisionBulk(decision: Decision): Promise<void> {
    const selectedItems = items.filter((item) => selectedKeys.has(item.key));
    if (selectedItems.length === 0) return;

    const response = await fetch("/api/evaluations", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        items: selectedItems.map((item) => ({
          slug: item.slug,
          job_id: item.job_id,
          ats: item.ats,
          decision,
        })),
      }),
    });

    if (!response.ok) {
      setError(`Could not save bulk decision (${response.status})`);
      return;
    }

    const selected = new Set(selectedItems.map((item) => item.key));
    setItems((prev) =>
      prev
        .map((row) => (selected.has(row.key) ? { ...row, decision } : row))
        .filter((row) => {
          if (decisionFilter === "all") return true;
          if (decisionFilter === "unclassified" && row.decision === null) return true;
          if (decisionFilter === row.decision) return true;
          return false;
        }),
    );
    setSelectedKeys(new Set());
  }

  function toggleSelected(key: string): void {
    setSelectedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  function selectVisible(): void {
    setSelectedKeys(new Set(items.map((item) => item.key)));
  }

  async function fetchDescription(item: OpportunityWithEvaluation): Promise<void> {
    setDescriptions((prev) => ({
      ...prev,
      [item.key]: { loading: true, text: prev[item.key]?.text ?? null, error: null },
    }));
    try {
      const response = await fetch("/api/jd-description", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          ats: item.ats,
          slug: item.slug,
          job_id: item.job_id,
          absolute_url: item.absolute_url,
          existing_description: item.description ?? null,
        }),
      });
      const payload = (await response.json()) as { description?: string; error?: string };
      if (!response.ok) {
        throw new Error(payload.error ?? `Request failed (${response.status})`);
      }
      setDescriptions((prev) => ({
        ...prev,
        [item.key]: { loading: false, text: payload.description ?? "", error: null },
      }));
    } catch (err) {
      setDescriptions((prev) => ({
        ...prev,
        [item.key]: { loading: false, text: null, error: String(err) },
      }));
    }
  }

  function getDecisionColor(decision: Decision | null): string {
    if (decision === "interested") return "tint-interested";
    if (decision === "not_interested") return "tint-alert";
    if (decision === "later") return "tint-success"; // Using lime/success for later per candy accents
    return "tint-neutral";
  }

  const decisionTabs: { value: DecisionFilter; label: string }[] = [
    { value: "unclassified", label: "UNCLASSIFIED" },
    { value: "interested", label: "INTERESTED" },
    { value: "not_interested", label: "PASS" },
    { value: "later", label: "LATER" },
    { value: "all", label: "ALL" },
  ];

  return (
    <>
      <header className="page-header">
        <span className="eyebrow">OPPORTUNITY REVIEW</span>
        <h1 className="h1">Eligible Roles</h1>
        <p className="muted-text">
          Review your pipeline. Mark roles you want to pursue.
        </p>
      </header>

      {/* Triage Tabs */}
      <div className="filter-tabs" style={{ marginBottom: "var(--s-md)" }}>
        {decisionTabs.map((tab) => (
          <button
            key={tab.value}
            className={`filter-tab ${decisionFilter === tab.value ? "active" : ""}`}
            onClick={() => {
              setDecisionFilter(tab.value);
              void loadData(locationFilter, tab.value, atsFilter, sortOrder);
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="toolbar">
        <input
          className="input"
          placeholder="Filter by location (e.g., latam)"
          value={locationFilter}
          onChange={(event) => setLocationFilter(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              void loadData(locationFilter, decisionFilter, atsFilter, sortOrder);
            }
          }}
        />
        <select
          className="select"
          value={atsFilter}
          onChange={(event) => {
            const value = event.target.value as AtsFilter;
            setAtsFilter(value);
            void loadData(locationFilter, decisionFilter, value, sortOrder);
          }}
        >
          <option value="all">ALL ATS</option>
          {atsOptions.map((ats) => (
            <option key={ats} value={ats}>
              {ats.toUpperCase()}
            </option>
          ))}
        </select>
        <select
          className="select"
          value={sortOrder}
          onChange={(event) => {
            const value = event.target.value as OpportunitySort;
            setSortOrder(value);
            void loadData(locationFilter, decisionFilter, atsFilter, value);
          }}
        >
          <option value="newest">NEWEST FIRST</option>
          <option value="oldest">OLDEST FIRST</option>
        </select>
      </div>

      <div className="chip-row">
        {locationTags.map((tag) => (
          <button
            key={tag}
            className="chip"
            onClick={() => {
              const next = tag === "unknown" ? "" : tag;
              setLocationFilter(next);
              void loadData(next, decisionFilter, atsFilter, sortOrder);
            }}
          >
            {formatLocationTagLabel(tag)}
          </button>
        ))}
        <button
          className="btn-ghost"
          style={{ padding: "4px 10px", fontSize: "0.75rem" }}
          onClick={() => {
            setLocationFilter("");
            setDecisionFilter("unclassified");
            setAtsFilter("all");
            void loadData("", "unclassified", "all", sortOrder);
          }}
        >
          RESET FILTERS
        </button>
      </div>

      <div className="summary-pills">
        <span className="mono-label">Showing {items.length}</span>
        
        {/* Conditional Summary Pills */}
        {summary.interested > 0 ? (
          <span className="badge-success">Interested: {summary.interested}</span>
        ) : (
          <span className="tag">Interested: 0</span>
        )}
        
        {summary.not_interested > 0 ? (
          <span className="badge-alert">Pass: {summary.not_interested}</span>
        ) : (
          <span className="tag">Pass: 0</span>
        )}
        
        {summary.later > 0 ? (
          <span className="badge-success" style={{ backgroundColor: "var(--purple)", color: "var(--on-primary)", border: "1px solid var(--ink)" }}>Later: {summary.later}</span>
        ) : (
          <span className="tag">Later: 0</span>
        )}
        
        <span className="tag">Unclassified: {summary.unclassified}</span>
      </div>

      {selectedKeys.size > 0 && (
        <div className="bulk-actions">
          <span className="mono-label">{selectedKeys.size} selected</span>
          <button className="btn-primary" onClick={() => void setDecisionBulk("interested")}>
            Mark Interested
          </button>
          <button className="btn-secondary" onClick={() => void setDecisionBulk("not_interested")}>
            Mark Pass
          </button>
          <button className="btn-ghost" onClick={() => setSelectedKeys(new Set())}>
            Clear
          </button>
        </div>
      )}

      {loading && <div className="description-loading">Loading opportunities...</div>}
      {error && <div className="description-error">{error}</div>}

      {!loading && !error && items.length === 0 && (
        <div className="empty-state">NO OPPORTUNITIES FOUND</div>
      )}

      <div className="card-list">
        {items.length > 0 && (
          <div className="bulk-select-row">
            <button className="btn-ghost" onClick={selectVisible}>
              Select visible
            </button>
            <button className="btn-ghost" onClick={() => setSelectedKeys(new Set())}>
              Deselect all
            </button>
          </div>
        )}
        {items.map((item) => {
          const descriptionState = descriptions[item.key];
          const updatedAt = formatUpdatedAt(item.updated_at);
          const decisionClass = getDecisionColor(item.decision);
          const isExpanded = !!expandedCards[item.key];
          
          return (
             <div
               key={item.key}
               className={`card ${isExpanded ? "is-expanded" : ""} ${
                 selectedKeys.has(item.key) ? "is-selected" : ""
               }`}
               onClick={() => toggleCard(item.key)}
             >
              <div className={`dog-ear ${decisionClass}`}></div>
              
              <div className="card-summary-view">
                <div className="card-summary-left">
                  <label className="card-checkbox-wrap" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      className="card-checkbox"
                      checked={selectedKeys.has(item.key)}
                      onChange={() => toggleSelected(item.key)}
                    />
                  </label>
                  <h3 className="card-summary-title"><strong>{item.title}</strong></h3>
                  <span className="mono-label muted-text">{item.slug} · {item.ats.toUpperCase()}</span>
                  <span className="tag">{item.location_raw ?? "unknown"}</span>
                </div>
                <div className="card-summary-meta">
                  {item.decision === "interested" && <span className="badge-success">INTERESTED</span>}
                  {item.decision === "not_interested" && <span className="badge-alert">PASS</span>}
                  {item.decision === "later" && <span className="tag">LATER</span>}
                </div>
              </div>
              
              {isExpanded && (
                <div className="card-content-wrapper">
                  <div className="card-main-info">
                    <div className="card-meta">
                      <span className="muted-text mono-label" title={updatedAt.tooltip}>
                        UPDATED {updatedAt.relative.toUpperCase()}
                      </span>
                    </div>

                    {item.matched_keywords && item.matched_keywords.length > 0 && (
                      <div className="card-keywords">
                        {item.matched_keywords.map((kw, i) => (
                          <span key={i} className="keyword">{kw}</span>
                        ))}
                      </div>
                    )}

                    {descriptionState?.loading && <div className="description-loading">LOADING DESCRIPTION...</div>}
                    {descriptionState?.error && (
                      <div className="description-error">
                        {descriptionState.error}
                      </div>
                    )}
                    {descriptionState?.text && (
                      <div className="description-box">{descriptionState.text}</div>
                    )}
                  </div>

                  <div className="card-side-actions">
                    <button 
                      className={`btn-primary ${item.decision === "interested" ? "is-active" : ""}`} 
                      onClick={(e) => { e.stopPropagation(); void setDecision(item, "interested"); }}
                    >
                      {DECISION_LABELS.interested}
                    </button>
                    <button 
                      className={`btn-secondary ${item.decision === "not_interested" ? "is-active" : ""}`} 
                      onClick={(e) => { e.stopPropagation(); void setDecision(item, "not_interested"); }}
                    >
                      {DECISION_LABELS.not_interested}
                    </button>
                    <button 
                      className={`btn-secondary ${item.decision === "later" ? "is-active" : ""}`} 
                      onClick={(e) => { e.stopPropagation(); void setDecision(item, "later"); }}
                    >
                      {DECISION_LABELS.later}
                    </button>
                    <button className="btn-ghost" onClick={(e) => { e.stopPropagation(); void fetchDescription(item); }}>
                      VIEW JD ↓
                    </button>
                    {item.absolute_url && (
                      <a href={item.absolute_url} target="_blank" rel="noreferrer" className="btn-ghost" onClick={(e) => e.stopPropagation()}>
                        OPEN URL ↗
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

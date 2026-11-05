"""Dashboard statistics and cross-investigation aggregation."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Investigation


def compute_dashboard_stats(db: Session) -> dict[str, Any]:
    rows = list(db.scalars(select(Investigation).order_by(Investigation.updated_at.desc())).all())
    total_investigations = len(rows)

    open_statuses = {"draft", "under_investigation", "pending_qa"}
    open_deviations = sum(1 for r in rows if r.status in open_statuses)
    in_progress = sum(1 for r in rows if r.status == "under_investigation")
    closed = sum(1 for r in rows if r.status in {"closed", "approved"})

    today_str = date.today().isoformat()
    total_capas = 0
    pending_capas = 0
    overdue_capas = 0
    completed_capas = 0

    severity_counts = {"critical": 0, "major": 0, "minor": 0, "unknown": 0}
    status_counts = {
        "draft": 0,
        "under_investigation": 0,
        "pending_qa": 0,
        "approved": 0,
        "closed": 0,
    }
    category_counts = {
        "Man": 0,
        "Machine": 0,
        "Method": 0,
        "Material": 0,
        "Measurement": 0,
        "Environment": 0,
        "Other": 0,
    }

    closure_times_days: list[float] = []

    for r in rows:
        sev = (r.severity or "unknown").lower()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["unknown"] += 1

        st = (r.status or "draft").lower()
        if st in status_counts:
            status_counts[st] += 1

        # Check closure time
        if r.status in {"closed", "approved"} and r.created_at and r.updated_at:
            delta = (r.updated_at - r.created_at).total_seconds() / 86400.0
            closure_times_days.append(max(0.1, round(delta, 1)))

        doc = r.document or {}

        # Aggregate CAPAs
        capas = doc.get("capas") or []
        for c in capas:
            total_capas += 1
            c_status = (c.get("status") or "proposed").lower()
            if c_status in {"completed", "verified"}:
                completed_capas += 1
            else:
                pending_capas += 1
                due = (c.get("due_date") or "").strip()
                if due and due < today_str:
                    overdue_capas += 1

        # Aggregate Categories from root causes & fishbone
        for cause in doc.get("root_causes") or []:
            cat = cause.get("category") or "Other"
            if cat in category_counts:
                category_counts[cat] += 1
            else:
                category_counts["Other"] += 1

        for bone in doc.get("fishbone") or []:
            cat = bone.get("category") or "Other"
            if cat in category_counts:
                category_counts[cat] += 1

    avg_closure_time_days = (
        round(sum(closure_times_days) / len(closure_times_days), 1) if closure_times_days else 0.0
    )
    capa_completion_rate = (
        round((completed_capas / total_capas) * 100, 1) if total_capas > 0 else 100.0
    )

    # Monthly activity trends (last 6 months)
    recent_items = [
        {
            "id": r.id,
            "deviation_number": r.deviation_number or "Unassigned",
            "title": r.title or "Untitled Deviation",
            "product_name": r.product_name or "Not recorded",
            "batch_lot": r.batch_lot or "N/A",
            "severity": r.severity or "unknown",
            "status": r.status or "draft",
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else "",
        }
        for r in rows[:10]
    ]

    return {
        "kpis": {
            "total_investigations": total_investigations,
            "open_deviations": open_deviations,
            "in_progress": in_progress,
            "pending_capas": pending_capas,
            "overdue_capas": overdue_capas,
            "closed_investigations": closed,
            "total_capas": total_capas,
            "capa_completion_rate": capa_completion_rate,
            "avg_closure_time_days": avg_closure_time_days,
        },
        "charts": {
            "severity_distribution": [
                {"label": "Critical", "count": severity_counts["critical"], "color": "#dc2626"},
                {"label": "Major", "count": severity_counts["major"], "color": "#d97706"},
                {"label": "Minor", "count": severity_counts["minor"], "color": "#2563eb"},
                {"label": "Unclassified", "count": severity_counts["unknown"], "color": "#64748b"},
            ],
            "category_distribution": [
                {"category": cat, "count": count}
                for cat, count in category_counts.items()
                if count > 0 or cat in {"Man", "Machine", "Method", "Material", "Measurement", "Environment"}
            ],
            "status_distribution": [
                {"status": "Draft", "count": status_counts["draft"]},
                {"status": "Under Investigation", "count": status_counts["under_investigation"]},
                {"status": "Pending QA", "count": status_counts["pending_qa"]},
                {"status": "Approved / Closed", "count": status_counts["approved"] + status_counts["closed"]},
            ],
        },
        "recent_investigations": recent_items,
    }


def get_all_cross_capas(db: Session) -> list[dict[str, Any]]:
    rows = list(db.scalars(select(Investigation).order_by(Investigation.updated_at.desc())).all())
    items: list[dict[str, Any]] = []
    for r in rows:
        doc = r.document or {}
        capas = doc.get("capas") or []
        for c in capas:
            items.append({
                "investigation_id": r.id,
                "deviation_number": r.deviation_number or "Unassigned",
                "product_name": r.product_name or "",
                "batch_lot": r.batch_lot or "",
                "capa_id": c.get("id") or "",
                "capa_type": c.get("capa_type") or "corrective",
                "description": c.get("description") or "",
                "rationale": c.get("rationale") or "",
                "owner": c.get("owner") or "",
                "due_date": c.get("due_date") or "",
                "effectiveness_check": c.get("effectiveness_check") or "",
                "status": c.get("status") or "proposed",
                "ai_suggested": c.get("ai_suggested", False),
                "confirmed": c.get("confirmed", False),
            })
    return items


def get_all_cross_evidence(db: Session) -> list[dict[str, Any]]:
    rows = list(db.scalars(select(Investigation).order_by(Investigation.updated_at.desc())).all())
    items: list[dict[str, Any]] = []
    for r in rows:
        doc = r.document or {}
        src = doc.get("source") or {}
        if src.get("raw_text") or src.get("filename"):
            items.append({
                "id": f"src_{r.id}",
                "investigation_id": r.id,
                "deviation_number": r.deviation_number or "Unassigned",
                "product_name": r.product_name or "",
                "title": src.get("filename") or f"Incident Ingestion ({src.get('kind', 'text')})",
                "kind": src.get("kind") or "text",
                "filename": src.get("filename") or "",
                "sender": src.get("sender") or "",
                "subject": src.get("subject") or "",
                "char_count": len(src.get("raw_text") or ""),
                "excerpt": (src.get("raw_text") or "")[:280] + ("…" if len(src.get("raw_text") or "") > 280 else ""),
                "status": "Verified Source Record",
                "classification": "Supporting",
            })
        for gap in doc.get("gaps") or []:
            items.append({
                "id": f"gap_{gap.get('id')}",
                "investigation_id": r.id,
                "deviation_number": r.deviation_number or "Unassigned",
                "product_name": r.product_name or "",
                "title": f"Gap: {gap.get('topic')}",
                "kind": "evidence_gap",
                "filename": gap.get("suggested_source") or "Required Documentation",
                "sender": "AI Evidence Audit",
                "subject": gap.get("why_it_matters") or "",
                "char_count": 0,
                "excerpt": f"Why it matters: {gap.get('why_it_matters', '')}. Suggested source: {gap.get('suggested_source', '')}",
                "status": "Evidence Missing" if not gap.get("resolved") else "Resolved",
                "classification": "Gap Requirement",
            })
    return items


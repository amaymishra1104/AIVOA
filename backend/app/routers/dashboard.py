from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.dashboard import (
    compute_dashboard_stats,
    get_all_cross_capas,
    get_all_cross_evidence,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)) -> dict:
    return compute_dashboard_stats(db)


@router.get("/capas")
def all_capas(db: Session = Depends(get_db)) -> dict:
    return {"capas": get_all_cross_capas(db)}


@router.get("/evidence")
def all_evidence(db: Session = Depends(get_db)) -> dict:
    return {"evidence": get_all_cross_evidence(db)}


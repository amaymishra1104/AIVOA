from app.schemas import RCARecord


def test_dashboard_stats_empty(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "charts" in data
    assert data["kpis"]["total_investigations"] == 0
    assert data["kpis"]["open_deviations"] == 0


def test_dashboard_stats_with_data(client):
    record = RCARecord().model_dump()
    record["deviation_number"] = {"value": "DEV-2026-901", "origin": "user", "confirmed": True}
    record["title"] = {"value": "Yield variation in reactor R-2", "origin": "user", "confirmed": True}
    record["product_name"] = {"value": "Atorvastatin calcium", "origin": "user", "confirmed": True}
    record["severity"] = {"value": "critical", "origin": "user", "confirmed": True}
    record["status"] = "under_investigation"
    record["capas"] = [
        {
            "id": "capa_1",
            "capa_type": "corrective",
            "description": "Recalibrate pressure sensor",
            "rationale": "Sensor drift observed",
            "owner": "Instrumentation",
            "due_date": "2026-12-01",
            "effectiveness_check": "Zero drift over 30 days",
            "status": "in_progress",
            "ai_suggested": False,
            "confirmed": True,
        }
    ]
    record["root_causes"] = [
        {
            "id": "cause_1",
            "statement": "Diaphragm rupture on control valve",
            "category": "Machine",
            "evidence": "Air leak detected",
            "confidence": "high",
            "evidence_supported": True,
            "grounded": True,
            "ai_suggested": False,
            "confirmed": True,
            "confirmed_by": "Lead QA",
        }
    ]

    create_res = client.post("/api/investigations", json={"record": record, "actor": "Test User"})
    assert create_res.status_code == 200

    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["kpis"]["total_investigations"] == 1
    assert data["kpis"]["in_progress"] == 1
    assert data["kpis"]["open_deviations"] == 1
    assert data["kpis"]["pending_capas"] == 1
    assert any(c["label"] == "Critical" and c["count"] == 1 for c in data["charts"]["severity_distribution"])

    # Test cross-capa list
    capas_res = client.get("/api/dashboard/capas")
    assert capas_res.status_code == 200
    capas = capas_res.json()["capas"]
    assert len(capas) == 1
    assert capas[0]["capa_id"] == "capa_1"
    assert capas[0]["deviation_number"] == "DEV-2026-901"

    # Test cross-evidence list
    ev_res = client.get("/api/dashboard/evidence")
    assert ev_res.status_code == 200
    assert "evidence" in ev_res.json()


from app.schemas import RCARecord
from app.services.grounding import evidence_grounded


def test_evidence_grounding_verification():
    source_text = (
        "Batch ATV-CA-26-0142 experienced a temperature excursion in crystallizer CR-300. "
        "The jacket temperature rose from 8°C to 17°C for 46 minutes while cooling valve V-17 was hunting. "
        "QC reported impurity RS-3 at 0.18% exceeding specification NMT 0.15%."
    )

    # Directly quoted statement with numbers
    assert evidence_grounded("jacket temperature rose from 8°C to 17°C for 46 minutes", source_text) is True

    # Quoted valve condition
    assert evidence_grounded("cooling valve V-17 was hunting", source_text) is True

    # Fabricated / halluncinated claim with non-existent numbers
    assert evidence_grounded("jacket temperature rose to 95°C for 180 minutes", source_text) is False

    # Irrelevant speculation not mentioned in source
    assert evidence_grounded("an operator fell asleep during the night shift", source_text) is False


def test_evidence_gap_aggregation(client):
    r = RCARecord().model_dump()
    r["deviation_number"] = {"value": "DEV-2026-GAP-TEST", "origin": "user", "confirmed": True}
    r["title"] = {"value": "Temperature excursion", "origin": "user", "confirmed": True}
    r["product_name"] = {"value": "Atorvastatin Calcium", "origin": "user", "confirmed": True}
    r["source"] = {
        "kind": "pdf",
        "filename": "DEV-2026-1184_atorvastatin_impurity.pdf",
        "raw_text": "Excursion observed during crystallization.",
    }
    r["gaps"] = [
        {
            "id": "gap_test_1",
            "topic": "Continuous SCADA Trend Chart for TIC-301",
            "why_it_matters": "Verify second-by-second ramp curve",
            "suggested_source": "SCADA Historian Archive",
            "origin": "ai",
            "resolved": False,
        }
    ]

    res = client.post("/api/investigations", json={"record": r, "actor": "Test QA"})
    assert res.status_code == 200

    ev_res = client.get("/api/dashboard/evidence")
    assert ev_res.status_code == 200
    evidence_items = ev_res.json()["evidence"]
    assert any(e["deviation_number"] == "DEV-2026-GAP-TEST" and e["kind"] == "evidence_gap" for e in evidence_items)


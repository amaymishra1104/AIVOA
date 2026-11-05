from app.schemas import RCARecord


def test_investigation_search_and_filter(client):
    # Insert 3 test investigations
    records = [
        ("DEV-2026-101", "Atorvastatin crystallization excursion", "Atorvastatin", "ATV-01", "critical", "under_investigation"),
        ("DEV-2026-102", "Metformin LOD failure", "Metformin HCl", "MFH-02", "major", "pending_qa"),
        ("DEV-2026-103", "Omeprazole wrong solvent staging", "Omeprazole", "OMP-03", "minor", "closed"),
    ]

    for dev_no, title, prod, lot, sev, status in records:
        r = RCARecord().model_dump()
        r["deviation_number"] = {"value": dev_no, "origin": "user", "confirmed": True}
        r["title"] = {"value": title, "origin": "user", "confirmed": True}
        r["product_name"] = {"value": prod, "origin": "user", "confirmed": True}
        r["batch_lot"] = {"value": lot, "origin": "user", "confirmed": True}
        r["severity"] = {"value": sev, "origin": "user", "confirmed": True}
        r["status"] = status
        res = client.post("/api/investigations", json={"record": r, "actor": "Test QA"})
        assert res.status_code == 200

    # 1. Search by query 'Atorvastatin'
    res = client.get("/api/investigations?q=Atorvastatin")
    assert res.status_code == 200
    items = res.json()["investigations"]
    assert len(items) == 1
    assert items[0]["deviation_number"] == "DEV-2026-101"

    # 2. Filter by severity 'critical'
    res = client.get("/api/investigations?severity=critical")
    assert res.status_code == 200
    items = res.json()["investigations"]
    assert len(items) == 1
    assert items[0]["deviation_number"] == "DEV-2026-101"

    # 3. Filter by status 'closed'
    res = client.get("/api/investigations?status=closed")
    assert res.status_code == 200
    items = res.json()["investigations"]
    assert len(items) == 1
    assert items[0]["deviation_number"] == "DEV-2026-103"

    # 4. Pagination limit=2
    res = client.get("/api/investigations?limit=2")
    assert res.status_code == 200
    items = res.json()["investigations"]
    assert len(items) == 2


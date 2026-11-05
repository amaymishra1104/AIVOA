from tests.fakes import SOURCE


def test_analyze_demo_mode(client):
    res = client.post(
        "/api/ai/analyze",
        json={"source_text": SOURCE, "source_kind": "text", "allow_demo": True},
    )
    assert res.status_code == 200
    data = res.json()
    assert "record" in data
    assert data["mode"] == "demo"
    assert "DEMO MODE" in data["assistant_message"]
    rec = data["record"]
    assert "Atorvastatin" in rec["product_name"]["value"]
    assert len(rec["whys"]) >= 3
    assert len(rec["fishbone"]) >= 3
    assert len(rec["capas"]) >= 2


def test_chat_demo_mode(client):
    res = client.post(
        "/api/ai/analyze",
        json={"source_text": SOURCE, "source_kind": "text", "allow_demo": True},
    )
    rec = res.json()["record"]

    chat_res = client.post(
        "/api/ai/chat",
        json={
            "message": "Why is this deviation classified as major?",
            "record": rec,
            "allow_demo": True,
        },
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "ICH Q9" in chat_data["assistant_message"]


from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.speakers.domain.entities import Speaker
from app.modules.speakers.infrastructure.repositories import SqlSpeakerRepository


def _seed_speaker(engine, name: str) -> int:
    with Session(engine) as s:
        repo = SqlSpeakerRepository(s)
        added = repo.add(Speaker(id=None, name=name, bio="", photo_url=""))
        return added.id


def test_list_speakers_returns_total_and_items(
    client: TestClient, engine
) -> None:
    _seed_speaker(engine, "Ada Lovelace")
    _seed_speaker(engine, "Grace Hopper")

    res = client.get("/api/speakers")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert {item["name"] for item in body["items"]} == {
        "Ada Lovelace",
        "Grace Hopper",
    }


def test_get_speaker_not_found_returns_404_with_code(client: TestClient) -> None:
    res = client.get("/api/speakers/9999")
    assert res.status_code == 404, res.text
    assert res.json()["code"] == "SPEAKER_NOT_FOUND"
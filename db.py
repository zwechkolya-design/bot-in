"""
db.py — Jaylar maǵlıwmatları ushın JSON tiykarındaǵı turaqlı saqlaw ornı.
"""
import json
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "places.json")


def _load() -> dict:
    if not os.path.exists(DB_PATH):
        return {"places": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_place(name: str, photos: list[str], phone: str, description: str) -> dict:
    """Jańa jay qosıw. photos - bul file_id qatarlarınıń dizimi."""
    data = _load()
    place = {
        "id": len(data["places"]) + 1,
        "name": name,
        "photos": photos,
        "phone": phone,
        "description": description,
    }
    data["places"].append(place)
    _save(data)
    return place


def get_all_places() -> list[dict]:
    return _load()["places"]


def get_place_by_name(name: str) -> Optional[dict]:
    for p in get_all_places():
        if p["name"].lower() == name.lower():
            return p
    return None


def get_place_by_id(place_id: int) -> Optional[dict]:
    for p in get_all_places():
        if p["id"] == place_id:
            return p
    return None


def update_place(place_id: int, **fields) -> Optional[dict]:
    """Jaydıń belgili bir bólimlerin jańalaw. Jańalanǵan jaydı yamasa None qaytaradı."""
    data = _load()
    for place in data["places"]:
        if place["id"] == place_id:
            place.update(fields)
            _save(data)
            return place
    return None


def delete_place(place_id: int) -> bool:
    data = _load()
    before = len(data["places"])
    data["places"] = [p for p in data["places"] if p["id"] != place_id]
    _save(data)
    return len(data["places"]) < before
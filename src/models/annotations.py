"""Gestion des annotations utilisateurs — stockage JSON local."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal

_STORE = Path(__file__).parent.parent.parent / "data" / "annotations.json"

AnnotationType = Literal["athlete", "pays", "sport", "edition"]


def _load() -> list[dict]:
    if not _STORE.exists():
        return []
    try:
        return json.loads(_STORE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(records: list[dict]) -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    _STORE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def get_annotations(
    annotation_type: AnnotationType | None = None,
    target: str | None = None,
) -> list[dict]:
    records = _load()
    if annotation_type:
        records = [r for r in records if r.get("type") == annotation_type]
    if target:
        records = [r for r in records if r.get("target") == target]
    return sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)


def add_annotation(
    annotation_type: AnnotationType,
    target: str,
    note: str,
    author: str = "Utilisateur",
    tags: list[str] | None = None,
) -> dict:
    records = _load()
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "type": annotation_type,
        "target": target,
        "note": note.strip(),
        "author": author.strip() or "Utilisateur",
        "tags": [t.strip() for t in (tags or []) if t.strip()],
    }
    records.append(entry)
    _save(records)
    return entry


def delete_annotation(annotation_id: str) -> bool:
    records = _load()
    filtered = [r for r in records if r.get("id") != annotation_id]
    if len(filtered) == len(records):
        return False
    _save(filtered)
    return True


def get_targets_for_type(annotation_type: AnnotationType) -> list[str]:
    records = _load()
    return sorted({r["target"] for r in records if r.get("type") == annotation_type})

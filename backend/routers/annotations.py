from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.models.annotations import add_annotation, get_annotations, delete_annotation, get_targets_for_type
from backend.deps import get_df

router = APIRouter()


class AnnotationIn(BaseModel):
    type: str
    target: str
    note: str
    author: Optional[str] = "Utilisateur"
    tags: Optional[str] = ""


@router.get("/")
def list_annotations(type: Optional[str] = None, target: Optional[str] = None):
    return get_annotations(type, target)


@router.post("/")
def create_annotation(body: AnnotationIn):
    ann = add_annotation(body.type, body.target, body.note, body.author, body.tags)
    return ann


@router.delete("/{ann_id}")
def remove_annotation(ann_id: str):
    ok = delete_annotation(ann_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return {"deleted": ann_id}


@router.get("/targets")
def targets(type: str):
    df = get_df()
    return get_targets_for_type(df, type)

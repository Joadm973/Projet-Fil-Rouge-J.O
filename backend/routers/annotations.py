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
    tags_list = [t.strip() for t in (body.tags or "").split(",") if t.strip()]
    ann = add_annotation(body.type, body.target, body.note, body.author, tags_list)
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
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    if type == "athlete":
        return sorted([str(x) for x in medals["Name"].dropna().unique()])
    elif type == "pays":
        return sorted([str(x) for x in medals["Team"].dropna().unique()])
    elif type == "sport":
        return sorted([str(x) for x in medals["Sport"].dropna().unique()])
    elif type == "edition":
        years = sorted(df["Year"].unique(), reverse=True)
        return [str(y) for y in years]
    return []

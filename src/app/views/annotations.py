"""Vue Annotations utilisateurs — avis et notes sur athlètes, pays, sports, éditions."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.app.components.cards import insight, section_header
from src.models.annotations import (
    add_annotation,
    delete_annotation,
    get_annotations,
)

_TYPE_LABELS = {
    "athlete": "Athlète",
    "pays": "Pays",
    "sport": "Sport",
    "edition": "Édition",
}

_TYPE_ICONS = {
    "athlete": "🏃",
    "pays": "🌍",
    "sport": "🏅",
    "edition": "📅",
}


def _annotation_card(ann: dict, df: pd.DataFrame) -> None:
    icon = _TYPE_ICONS.get(ann["type"], "📝")
    label = _TYPE_LABELS.get(ann["type"], ann["type"])
    ts = ann.get("timestamp", "")[:16].replace("T", " ")
    author = ann.get("author", "Utilisateur")
    tags = ann.get("tags", [])

    with st.container():
        col_main, col_del = st.columns([10, 1])
        with col_main:
            st.markdown(
                f"""
                <div style="
                    border:1px solid rgba(255,255,255,0.1);
                    border-radius:8px;
                    padding:12px 16px;
                    margin-bottom:8px;
                    background:rgba(255,255,255,0.03);
                ">
                    <div style="font-size:0.78rem; opacity:0.6; margin-bottom:4px;">
                        {icon} <strong>{label}</strong> · {ann['target']}
                        &nbsp;&nbsp;·&nbsp;&nbsp; {author}
                        &nbsp;&nbsp;·&nbsp;&nbsp; {ts}
                    </div>
                    <div style="font-size:0.96rem; line-height:1.5;">{ann['note']}</div>
                    {"<div style='margin-top:6px;'>" + " ".join(f"<span style='background:rgba(30,136,229,0.2);border-radius:4px;padding:2px 7px;font-size:0.72rem;margin-right:4px;'>{t}</span>" for t in tags) + "</div>" if tags else ""}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("✕", key=f"del_{ann['id']}", help="Supprimer cette annotation"):
                delete_annotation(ann["id"])
                st.rerun()


def show(df: pd.DataFrame) -> None:
    st.title("📝 Annotations & avis utilisateurs")
    st.markdown(
        "Ajoutez des notes personnelles sur des **athlètes**, **pays**, **disciplines** "
        "ou **éditions olympiques**. Ces annotations sont sauvegardées localement."
    )

    # ── Formulaire d'ajout ────────────────────────────────────────────────
    section_header("Ajouter une annotation")

    with st.form("form_add_annotation", clear_on_submit=True):
        col_f1, col_f2 = st.columns([1, 2])

        with col_f1:
            ann_type = st.selectbox(
                "Type",
                options=list(_TYPE_LABELS.keys()),
                format_func=lambda k: f"{_TYPE_ICONS[k]} {_TYPE_LABELS[k]}",
            )
            author = st.text_input("Auteur", value="Utilisateur", max_chars=40)
            tags_raw = st.text_input(
                "Tags (séparés par des virgules)",
                placeholder="record, à_surveiller, 2028…",
            )

        with col_f2:
            # Suggestions selon le type
            medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]

            if ann_type == "athlete":
                suggestions = sorted(medals["Name"].dropna().unique())
                target = st.selectbox("Athlète", suggestions, key="form_target_ath")
            elif ann_type == "pays":
                suggestions = sorted(medals["Team"].dropna().unique())
                target = st.selectbox("Pays", suggestions, key="form_target_pays")
            elif ann_type == "sport":
                suggestions = sorted(medals["Sport"].dropna().unique())
                target = st.selectbox("Sport", suggestions, key="form_target_sport")
            else:  # edition
                years = sorted(df["Year"].unique(), reverse=True)
                target = st.selectbox(
                    "Édition",
                    [str(y) for y in years],
                    key="form_target_ed",
                )

            note = st.text_area(
                "Note / avis",
                height=120,
                placeholder="Entrez votre observation, analyse ou remarque ici…",
                max_chars=1000,
            )

        submitted = st.form_submit_button("Enregistrer", type="primary", use_container_width=True)

    if submitted:
        if not note.strip():
            st.warning("La note ne peut pas être vide.")
        else:
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            add_annotation(ann_type, target, note, author=author, tags=tags)
            st.success(f"Annotation enregistrée sur **{target}**.")
            st.rerun()

    st.markdown("---")

    # ── Filtres & liste ───────────────────────────────────────────────────
    section_header("Annotations enregistrées")

    all_ann = get_annotations()

    if not all_ann:
        st.info("Aucune annotation pour le moment. Utilisez le formulaire ci-dessus pour en ajouter.")
        return

    # Filtres
    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f1:
        filter_type = st.selectbox(
            "Filtrer par type",
            ["Tous"] + list(_TYPE_LABELS.keys()),
            format_func=lambda k: "Tous" if k == "Tous" else f"{_TYPE_ICONS[k]} {_TYPE_LABELS[k]}",
        )
    with col_f2:
        search_term = st.text_input("Rechercher dans les notes ou cibles", placeholder="Phelps, Natation…")
    with col_f3:
        st.metric("Total annotations", len(all_ann))

    # Appliquer filtres
    filtered = all_ann
    if filter_type != "Tous":
        filtered = [a for a in filtered if a["type"] == filter_type]
    if search_term.strip():
        q = search_term.strip().lower()
        filtered = [
            a for a in filtered
            if q in a.get("target", "").lower()
            or q in a.get("note", "").lower()
            or any(q in t.lower() for t in a.get("tags", []))
        ]

    if not filtered:
        st.info("Aucune annotation ne correspond aux filtres.")
        return

    st.caption(f"{len(filtered)} annotation(s) affichée(s)")

    for ann in filtered:
        _annotation_card(ann, df)

    # ── Stats rapides ─────────────────────────────────────────────────────
    if len(all_ann) >= 3:
        st.markdown("---")
        section_header("Résumé de vos annotations")

        ann_df = pd.DataFrame(all_ann)
        by_type = ann_df["type"].value_counts().rename(index=_TYPE_LABELS)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**Par type**")
            for t, cnt in by_type.items():
                st.markdown(f"- {t}: **{cnt}**")

        with col_s2:
            top_targets = ann_df["target"].value_counts().head(5)
            st.markdown("**Cibles les plus annotées**")
            for target, cnt in top_targets.items():
                st.markdown(f"- {target}: **{cnt}**")

        insight(
            "Ces annotations sont stockées dans <code>data/annotations.json</code>. "
            "Elles persistent entre les sessions et peuvent être partagées avec votre équipe."
        )

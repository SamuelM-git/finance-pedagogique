import streamlit as st


ETAPES = [
    "budget",
    "epargne",
    "investissement",
    "quiz",
]


def init_progress():
    """Initialise les variables de session."""
    if "budget_data" not in st.session_state:
        st.session_state.budget_data = {
            "reste": 0,
            "depenses": {},
        }

    if "etapes" not in st.session_state:
        st.session_state.etapes = {
            etape: False for etape in ETAPES
        }

    if "xp" not in st.session_state:
        st.session_state.xp = 0

    if "badges" not in st.session_state:
        st.session_state.badges = []

    if "initial_budget" not in st.session_state:
        st.session_state.initial_budget = {}

    if "objectif" not in st.session_state:
        st.session_state.objectif = 0


def valider_etape(etape, xp=0, badge=None):
    """
    Valide une étape et ajoute XP + badge si nécessaire.

    :param etape: str
    :param xp: int
    :param badge: str | None
    """
    if etape not in st.session_state.get("etapes", {}):
        return

    # Évite de donner plusieurs fois les récompenses
    if not st.session_state.etapes[etape]:
        st.session_state.etapes[etape] = True
        st.session_state.xp += xp

        if badge:
            badges = st.session_state.get("badges", [])
            if badge not in badges:
                badges.append(badge)
                st.session_state.badges = badges


def add_xp(points):
    """
    Ajoute des points d'expérience.

    :param points: int
    """
    st.session_state.xp = st.session_state.get("xp", 0) + points


def afficher_barre_progression():
    """Affiche la progression globale."""
    etapes = st.session_state.get("etapes", {})

    total = len(etapes)
    valides = sum(etapes.values())

    progression = valides / total if total > 0 else 0

    st.markdown("## 🎯 Progression du parcours")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.progress(progression)

    with col2:
        st.metric("Avancement", f"{progression * 100:.0f}%")

    st.caption(f"{valides} étapes validées sur {total}")


def afficher_xp():
    """Affiche le niveau et la progression XP."""
    xp = st.session_state.get("xp", 0)

    niveau = xp // 100 + 1
    progression_niveau = (xp % 100) / 100

    st.markdown(
        f"""
        <div class="card">
            <h3>⭐ Niveau {niveau}</h3>
            <p>XP total : <b>{xp}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(progression_niveau)


def afficher_badges_sidebar():
    """Affiche les badges dans la sidebar."""
    st.sidebar.markdown("## 🏅 Tes badges")

    badges = st.session_state.get("badges", [])

    if not badges:
        st.sidebar.info("Aucun badge débloqué pour le moment.")
        return

    for badge in badges:
        st.sidebar.markdown(
            f"""
            <div style="
                background:#FACC15;
                color:#1E293B;
                padding:12px;
                border-radius:18px;
                font-weight:700;
                margin-bottom:12px;
                text-align:center;">
                🏅 {badge}
            </div>
            """,
            unsafe_allow_html=True,
        )

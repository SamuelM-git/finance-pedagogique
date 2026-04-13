import streamlit as st

from modules import (
    module_budget,
    module_epargne,
    module_investissement,
    module_quiz,
)

from progress import (
    init_progress,
    afficher_badges_sidebar,
)


MODULES = {
    "budget": module_budget.module_budget,
    "epargne": module_epargne.module_epargne,
    "investissement": module_investissement.module_investissement,
    "quiz": module_quiz.module_quiz,
}


def main():
    """Point d'entrée principal de l'application."""
    st.set_page_config(
        page_title="Finance LudiK - Samuel M",
        page_icon="🏦",
        layout="wide",
    )

    init_progress()

    if "module" not in st.session_state:
        st.session_state.module = "budget"

    afficher_header()
    afficher_navigation()
    afficher_module_actif()
    afficher_sidebar()


def afficher_header():
    """Affiche le header principal."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg,#2563EB,#7C3AED);
            padding:50px;
            border-radius:30px;
            color:white;
            margin-bottom:40px;
            text-align:center;
        ">
            <h1>🏦 Finance LudiK</h1>
            <p style="font-size:18px;">
                Budget  •  Épargne  •  Investissement
            </p>
            <p style="font-size:18px;">
                • Quiz •
            </p>
            <p style="font-size:18px;">
                Par Samuel M, Data Analyst pour aider à la décision
            </p>
            <p style="font-size:14px;">
                Mes liens :
                <a href="https://github.com/SamuelM-git/finance-pedagogique"
                    target="_blank" style="color:white;">
                    GitHub
                </a>
                -
                <a href="https://www.linkedin.com/in/samuel-m-co/"
                    target="_blank" style="color:white;">
                    LinkedIn
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def afficher_navigation():
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #2563EB;
            color: white;
            border-radius: 10px;
            border: none;
            height: 45px;
            font-weight: 600;
        }

        div.stButton > button:hover {
            background-color: #1D4ED8;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        """
        Les informations et outils proposés ont une finalité exclusivement
        pédagogique et informative. Les données saisies sont traitées
        temporairement, sans stockage. Les résultats fournis sont des
        simulations indicatives et ne constituent pas un conseil financier
        personnalisé ni un service de conseil en investissement.
        L'utilisateur reste seul responsable des décisions prises sur
        cette base.
        """
    )

    st.markdown("## 🧭 Choisis ton module")

    cols = st.columns(4)

    modules_info = [
        ("📊 Budget", "budget"),
        ("💰 Épargne", "epargne"),
        ("📈 Investissement", "investissement"),
        ("🧠 Quiz", "quiz"),
    ]

    for col, (label, mod) in zip(cols, modules_info):
        is_active = st.session_state.module == mod

        if col.button(
            label,
            key=f"btn_{mod}",
            type="primary" if is_active else "secondary",
        ):
            if st.session_state.module != mod:
                st.session_state.module = mod
                st.rerun()

    st.markdown("---")


def afficher_module_actif():
    """Affiche le module actuellement sélectionné."""
    module = st.session_state.module

    if module in MODULES:
        MODULES[module]()
    else:
        st.info("Module à développer...")


def afficher_sidebar():
    """Affiche le résumé XP et badges."""
    st.sidebar.title("📊 Progression")

    st.sidebar.metric(
        label="XP total",
        value=st.session_state.xp,
    )

    afficher_badges_sidebar()


if __name__ == "__main__":
    main()

import streamlit as st


def init_session():
    """Initialise les clés de session utilisées dans tous les modules."""
    if "budget_data" not in st.session_state:
        st.session_state.budget_data = {}
    if "etapes" not in st.session_state:
        st.session_state.etapes = {}
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "badges" not in st.session_state:
        st.session_state.badges = []
    if "module" not in st.session_state:
        st.session_state.module = "Budget"
    if "objectif" not in st.session_state:
        st.session_state.objectif = 0

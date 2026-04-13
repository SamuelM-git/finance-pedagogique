import streamlit as st
import random
import time


# -------------------------
# Banque de questions (15 par profil)
# -------------------------
BASE_QUESTIONS = {
    "Débutant": [
        ("Pourquoi épargner ?", ["Sécurité", "Dépenser"], "Sécurité"),
        ("Un budget sert à ?", ["Suivre ses dépenses", "Ignorer son argent"],
         "Suivre ses dépenses"),
        ("Une dépense fixe est ?", ["Prévisible", "Imprévisible"],
         "Prévisible"),
        ("Loyer est une ?", ["Charge fixe", "Loisir"], "Charge fixe"),
        ("Pourquoi suivre ses dépenses ?",
         ["Mieux gérer son argent", "Dépenser plus"],
         "Mieux gérer son argent"),
        ("Un revenu est ?", ["Argent reçu", "Argent dépensé"],
         "Argent reçu"),
        ("Épargner signifie ?",
         ["Mettre de côté", "Tout dépenser"],
         "Mettre de côté"),
        ("Une dépense variable est ?", ["Changeante", "Fixe"],
         "Changeante"),
        ("Courses alimentaires sont ?",
         ["Dépense variable", "Revenu"],
         "Dépense variable"),
        ("Pourquoi éviter les dettes ?",
         ["Coût élevé", "Aucun impact"],
         "Coût élevé"),
        ("Un objectif financier sert à ?", ["Planifier", "Ignorer"],
         "Planifier"),
        ("Économiser permet ?",
         ["Préparer l'avenir", "Perdre argent"],
         "Préparer l'avenir"),
        ("Un imprévu nécessite ?", ["Épargne", "Crédit obligatoire"],
         "Épargne"),
        ("Un abonnement est ?", ["Dépense récurrente", "Unique"],
         "Dépense récurrente"),
        ("Gérer son budget permet ?",
         ["Éviter découvert", "Dépenser plus"],
         "Éviter découvert"),
    ],

    "Prudent": [
        ("Un ETF permet ?", ["Diversifier", "Garantir un gain"],
         "Diversifier"),
        ("L'inflation fait quoi ?",
         ["Réduit pouvoir d'achat", "Augmente richesse"],
         "Réduit pouvoir d'achat"),
        ("Diversifier sert à ?", ["Réduire risque", "Augmenter risque"],
         "Réduire risque"),
        ("Un rendement est ?", ["Gain potentiel", "Perte certaine"],
         "Gain potentiel"),
        ("Un livret A est ?", ["Sécurisé", "Risque élevé"],
         "Sécurisé"),
        ("Le risque faible donne ?",
         ["Faible rendement", "Fort rendement"],
         "Faible rendement"),
        ("L'investissement long terme ?",
         ["Réduit volatilité", "Augmente risque"],
         "Réduit volatilité"),
        ("Une obligation est ?", ["Un prêt", "Une action"],
         "Un prêt"),
        ("Un portefeuille est ?",
         ["Ensemble d'actifs", "Compte bancaire"],
         "Ensemble d'actifs"),
        ("Plus de rendement implique ?",
         ["Plus de risque", "Moins de risque"],
         "Plus de risque"),
        ("L'épargne de précaution ?",
         ["Sécurité", "Investissement risqué"],
         "Sécurité"),
        ("SCPI correspond à ?", ["Immobilier", "Crypto"],
         "Immobilier"),
        ("Un ETF Monde investit ?",
         ["Globalement", "Localement"],
         "Globalement"),
        ("Inflation élevée ?",
         ["Diminue valeur argent", "Augmente valeur"],
         "Diminue valeur argent"),
        ("Un placement sûr ?",
         ["Rendement faible", "Rendement élevé"],
         "Rendement faible"),
    ],

    "Dynamique": [
        ("Intérêt composé ?",
         ["Effet boule de neige", "Effet négatif"],
         "Effet boule de neige"),
        ("Long terme réduit ?", ["Risque", "Gain"], "Risque"),
        ("Actions = ?", ["Part entreprise", "Dette"],
         "Part entreprise"),
        ("ETF S&P 500 suit ?",
         ["Marché US", "Marché Europe"],
         "Marché US"),
        ("Risque élevé ?",
         ["Potentiel élevé", "Gain garanti"],
         "Potentiel élevé"),
        ("Diversification ?",
         ["Réduit risque", "Augmente risque"],
         "Réduit risque"),
        ("Investir tôt ?",
         ["Maximise gains", "Aucun impact"],
         "Maximise gains"),
        ("Marché volatile ?",
         ["Fluctuations", "Stable"],
         "Fluctuations"),
        ("Plus rendement long terme ?",
         ["Actions", "Livret"],
         "Actions"),
        ("Capitalisation ?",
         ["Réinvestir gains", "Retirer gains"],
         "Réinvestir gains"),
        ("ETF = ?", ["Panier d'actifs", "Compte"],
         "Panier d'actifs"),
        ("Risque court terme ?", ["Élevé", "Faible"],
         "Élevé"),
        ("Immobilier rendement ?",
         ["Loyers", "Salaire"],
         "Loyers"),
        ("Marché baissier ?",
         ["Opportunité", "Fin investissement"],
         "Opportunité"),
        ("Stratégie long terme ?",
         ["Patience", "Timing"],
         "Patience"),
    ],
}


# -------------------------
# Génération des questions
# -------------------------
def generer_questions(profil):
    base = BASE_QUESTIONS[profil]
    questions = []

    for q, options, answer in base:
        opts = options.copy()
        random.shuffle(opts)

        questions.append({
            "q": q,
            "options": opts,
            "answer": answer,
        })

    random.shuffle(questions)
    return questions


# -------------------------
# Module principal
# -------------------------
def module_quiz():

    st.markdown("### 🧠 Quiz progressif")

    # -------------------------
    # Initialisation SAFE
    # -------------------------
    st.session_state.setdefault("xp", 0)
    st.session_state.setdefault("badges", [])
    st.session_state.setdefault("quiz_index", 0)
    st.session_state.setdefault("quiz_score", 0)
    st.session_state.setdefault("quiz_questions", [])
    st.session_state.setdefault("quiz_profil", None)
    st.session_state.setdefault("quiz_timer", time.time())

    # -------------------------
    # Profil
    # -------------------------
    profil = st.radio(
        "Choisis un profil et teste tes connaissances !",
        ["Débutant", "Prudent", "Dynamique"],
        horizontal=True,
        index=None
    )

    # Bloquer si pas de profil sélectionné
    if profil is None:
        st.info("👆 Sélectionne un profil pour commencer le quiz.")
        return

    # Reset si changement
    if st.session_state.quiz_profil != profil:
        st.session_state.quiz_profil = profil
        st.session_state.quiz_questions = generer_questions(profil)
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_timer = time.time()

    questions = st.session_state.quiz_questions
    index = st.session_state.quiz_index
    total = len(questions)

    # Progression
    if total > 0:
        st.progress(index / total)

    # -------------------------
    # Question
    # -------------------------
    if index < total:

        q = questions[index]

        st.markdown(f"### Question {index + 1}/{total}")
        st.markdown(q["q"])

        choix = st.radio(
            "Ta réponse",
            q["options"],
            key=f"quiz_{index}",
        )

        # Timer
        temps_limite = 10
        temps_ecoule = int(time.time() -
                           st.session_state.quiz_timer)
        temps_restant = max(0, temps_limite - temps_ecoule)

        st.markdown(f"⏱️ Temps restant : **{temps_restant}s**")

        # Temps écoulé
        if temps_restant <= 0:
            st.error("⏱️ Temps écoulé !")
            st.session_state.quiz_index += 1
            st.session_state.quiz_timer = time.time()
            st.rerun()

        # Validation
        if st.button("➡️ Valider et continuer"):

            if choix == q["answer"]:
                st.success("✅ Bonne réponse")
                st.session_state.quiz_score += 1
                st.session_state.xp += 2
            else:
                st.error("❌ Mauvaise réponse")

            st.session_state.quiz_index += 1
            st.session_state.quiz_timer = time.time()
            st.rerun()

    # -------------------------
    # Fin
    # -------------------------
    else:

        st.success("🎉 Quiz terminé !")

        score = st.session_state.quiz_score
        st.markdown(f"### 🎯 Score : {score} / {total}")

        if score > total * 0.8:
            st.success("🔥 Excellent niveau !")
        elif score > total * 0.5:
            st.info("👍 Bon niveau")
        else:
            st.warning("📚 Continue d'apprendre")

        if score > total * 0.7:
            if "🧠 Master Finance" not in st.session_state.badges:
                st.session_state.badges.append("🧠 Master Finance")

        if st.button("🔄 Recommencer le quiz"):
            keys_to_delete = [
                "quiz_index",
                "quiz_score",
                "quiz_questions",
                "quiz_profil",
                "quiz_timer",
            ]

            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()

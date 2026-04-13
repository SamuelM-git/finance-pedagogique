import streamlit as st
import matplotlib.pyplot as plt


# -------------------------
# Projection investissement
# -------------------------
def projection_investissement(mensuel, rendement):

    annees = list(range(1, 21))
    capital = []
    total = 0

    for _ in annees:
        total = (total + mensuel * 12) * (1 + rendement / 100)
        capital.append(total)

    return annees, capital


# -------------------------
# Projection inflation
# -------------------------
def projection_inflation(capital, inflation):

    capital_reel = []

    for i, val in enumerate(capital, start=1):
        reel = val / ((1 + inflation / 100) ** i)
        capital_reel.append(reel)

    return capital_reel


# -------------------------
# Comparaison placements
# -------------------------
def comparaison_placements(mensuel):

    placements = {
        "Livret A (~3% indicatif)": 3,
        "Immobilier (~5% indicatif)": 5,
        "ETF Monde (~7% indicatif)": 7,
    }

    resultats = {}

    for nom, rendement in placements.items():

        _, capital = projection_investissement(
            mensuel,
            rendement,
        )

        resultats[nom] = capital[-1]

    return resultats


# -------------------------
# Bloc pédagogique interactif
# -------------------------
def afficher_bloc_investissement(titre, description, exemples,
                                 rendement_defaut):

    if st.button(titre):

        st.markdown(f"### {titre}")

        st.write(description)

        st.markdown("**Exemples :**")
        for ex in exemples:
            st.write(f"- {ex}")

        st.markdown("#### 📊 Simulation")

        montant = st.slider(
            f"Montant mensuel pour {titre}",
            0.0,
            1000.0,
            100.0,
            key=f"slider_{titre}"
        )

        rendement = st.slider(
            f"Rendement (%) pour {titre}",
            0.0,
            10.0,
            rendement_defaut,
            key=f"rendement_{titre}"
        )

        annees, capital = projection_investissement(
            montant,
            rendement,
        )

        fig, ax = plt.subplots()

        ax.plot(annees, capital, marker="o")

        ax.set_title(f"Simulation {titre}")
        ax.set_xlabel("Années")
        ax.set_ylabel("Capital (€)")
        ax.grid(True)

        st.pyplot(fig)
        plt.close(fig)


# -------------------------
# Module principal
# -------------------------
def module_investissement():

    st.error("### Attention : tout investissement comporte un risque de "
             "perte partielle ou totale de votre capital !")
    st.warning(
            "Vous devez investir avec prudence et bien comprendre les risques"
            " associés. \nVous avez probablement déjà entendu l'expression "
            "« n'investissez jamais plus que ce que vous êtes prêt à perdre »"
        )

    st.info(
        "Les exemples et simulations proposés sont purement pédagogiques et "
        "ne constituent pas des recommandations d’investissement. Les "
        "rendements affichés sont hypothétiques et non garantis."
    )
    # -------------------------
    # Définition ajoutée
    # -------------------------
    st.markdown("### 📚 Qu'est-ce que l'investissement ?")

    st.info(
        "Investir consiste à placer de l'argent dans un actif dans "
        "le but de le faire fructifier sur le long terme. "
        "Contrairement à l'épargne, l'investissement comporte un "
        "niveau de risque mais offre généralement un rendement plus élevé."
    )

    st.write(
        "L'investissement reposerait sur 3 piliers essentiels :\n"
        "- 📆 Le temps (plus tu investis tôt, mieux c'est)\n"
        "- 📈 Le rendement\n"
        "- ⚠️ Le risque\n"
        "\nJe rajouterais un 4ème pilier : La diversification (ne pas "
        "mettre tous ses œufs dans le même panier)"
    )

    if "budget_data" not in st.session_state:

        st.info(
            "Analyse d'abord ton budget et ton épargne."
        )

        return

    reste = st.session_state.budget_data.get("reste", 0)

    if reste <= 0:

        st.warning(
            "Ton reste mensuel est nul ou négatif. "
            "Commence par améliorer ton budget."
        )

        return

    # -------------------------
    # Profil investisseur
    # -------------------------
    st.markdown("### 🧠 Ton profil investisseur")

    st.markdown("💡 Ton profil influence le type "
                "d'investissements adaptés et ton horizon de placement.")

    profil = st.radio(
        "Quel est ton profil ?",
        ["Débutant", "Prudent", "Dynamique"],
        horizontal=True
    )

    # Sauvegarde
    st.session_state["profil_investisseur"] = profil

    # Définition + rendement conseillé
    if profil == "Débutant":
        st.info(
            "🟢 Profil débutant : tu privilégies la sécurité et "
            "la stabilité. Tu acceptes peu de risque."
        )
        rendement_conseille = 3.0

    elif profil == "Prudent":
        st.info(
            "🔵 Profil prudent : tu cherches un équilibre entre "
            "risque et rendement."
        )
        rendement_conseille = 5.0
    else:
        st.info(
            "🔴 Profil dynamique : tu acceptes des variations "
            "importantes pour viser un rendement élevé."
        )
        rendement_conseille = 7.0

    # -------------------------
    # Recommandations profil
    # -------------------------
    st.markdown("### 🎯 Suggestions selon ton profil")

    if profil == "Débutant":
        st.success(
            "✔️ À titre indicatif, il est souvent suggéré de se tourner "
            "vers des placements simples et relativement sécurisés :\n"
            "- Livrets réglementés\n"
            "- ETF larges (monde)\n"
            "- Assurance vie fonds euros"
        )

    elif profil == "Prudent":
        st.success(
            "✔️ Tu peux équilibrer ton portefeuille :\n"
            "- ETF diversifiés\n"
            "- Immobilier (SCPI)\n"
            "- Obligations"
        )
    else:
        st.success(
            "✔️ À titre indicatif, certains investisseurs recherchent "
            "une performance à long terme :\n"
            "- ETF actions\n"
            "- Actions individuelles\n"
            "- Immobilier dynamique"
        )

    # -------------------------
    # Simulation principale
    # -------------------------
    st.markdown("### 💰 Montant à investir")

    investissement = st.slider(
        "Combien veux-tu investir chaque mois ?",
        0.0,
        float(reste),
        float(reste * 0.3),
    )

    rendement = st.slider(
        "Rendement annuel estimé (%)",
        0.0,
        10.0,
        rendement_conseille,  # ← dynamique
    )

    annees, capital = projection_investissement(
        investissement,
        rendement,
    )

    fig, ax = plt.subplots()

    ax.plot(
        annees,
        capital,
        marker="o",
        label="Capital"
    )

    ax.set_title("Projection de ton investissement")
    ax.set_xlabel("Années")
    ax.set_ylabel("Capital (€)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # -------------------------
    # Inflation
    # -------------------------
    st.markdown("### 📉 Impact de l'inflation")

    inflation = st.slider(
        "Inflation annuelle (%)",
        0.0,
        6.0,
        2.0,
        step=0.1,
    )

    capital_reel = projection_inflation(
        capital,
        inflation,
    )

    fig_inf, ax_inf = plt.subplots()

    ax_inf.plot(annees, capital, label="Capital nominal")
    ax_inf.plot(annees, capital_reel, label="Capital réel")

    ax_inf.set_title("Impact de l'inflation")
    ax_inf.set_xlabel("Années")
    ax_inf.set_ylabel("Valeur réelle (€)")
    ax_inf.legend()
    ax_inf.grid(True)

    st.pyplot(fig_inf)

    # -------------------------
    # Comparaison
    # -------------------------
    st.markdown("### ⚖️ Comparaison de placements")

    comparatif = comparaison_placements(investissement)

    fig_comp, ax_comp = plt.subplots()

    noms = list(comparatif.keys())
    valeurs = list(comparatif.values())

    ax_comp.bar(noms, valeurs, color="#2563EB")

    ax_comp.set_title("Capital après 20 ans")
    ax_comp.set_ylabel("Capital (€)")

    st.pyplot(fig_comp)

    # -------------------------
    # Bloc interactif
    # -------------------------
    st.markdown("---")
    st.markdown("### 🎯 Explorer les types d'investissement")

    afficher_bloc_investissement(
        "ETF",
        "Un ETF est un panier d'actions permettant de diversifier "
        "facilement son investissement.",
        ["ETF MSCI World", "ETF S&P 500"],
        7.0
    )

    afficher_bloc_investissement(
        "Immobilier",
        "L'immobilier consiste à investir dans des biens physiques "
        "pour générer des loyers ou une plus-value.",
        ["Location d'appartement", "SCPI"],
        5.0
    )

    afficher_bloc_investissement(
        "Actions",
        "Acheter une action revient à posséder une part d'entreprise.",
        ["Apple", "LVMH"],
        7.0
    )

    afficher_bloc_investissement(
        "Obligations",
        "Les obligations sont des prêts faits à des États ou entreprises.",
        ["Obligations d'État", "Obligations d'entreprise"],
        3.0
    )

    st.error("### Attention : tout investissement comporte un risque de "
             "perte partielle ou totale de votre capital !")

    plt.close(fig)
    plt.close(fig_inf)
    plt.close(fig_comp)

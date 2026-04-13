import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from modules.module_budget import dessiner_texte_multiligne

DISCLAIMER = (
    "Les informations et outils proposés ont une finalité exclusivement"
    " pédagogique et informative. Les données saisies sont traitées"
    " temporairement, sans stockage. Les résultats fournis sont des"
    " simulations indicatives et ne constituent pas un conseil financier"
    " personnalisé ni un service de conseil en investissement."
    " L'utilisateur reste seul responsable des décisions prises sur"
    " cette base."
)


# ----------------------
# Graphique intérêts composés
# ----------------------
def creer_graphique_interets_composes(epargne_mensuelle, taux):
    annees = list(range(1, 11))
    capital_simple = [epargne_mensuelle * 12 * an for an in annees]
    capital_composes = []
    total = 0
    for an in annees:
        total = (total + epargne_mensuelle * 12) * (1 + taux / 100)
        capital_composes.append(total)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(annees, capital_simple, marker="o", label="Sans intérêts")
    ax.plot(annees,
            capital_composes,
            marker="o",
            label="Avec intérêts composés")
    ax.set_xlabel("Années")
    ax.set_ylabel("Montant (€)")
    ax.set_title("Évolution de l'épargne")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    return fig, annees, capital_simple, capital_composes


# ----------------------
# PDF intégrant projection
# ----------------------
def generer_pdf_epargne(epargne_mensuelle, taux, fig_composes,
                        donnees_tableau, objectif=None, fig_proj=None):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Header
    pdf.setFillColor(colors.HexColor("#2563EB"))
    pdf.rect(0, height - 60, width, 60, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 16)
    pdf.drawString(40, height - 32, "Finance LudiK — Le module épargne")
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(40, height - 48, "Par Samuel M, Data Analyst pour aider à"
                                    " la décision")
    pdf.setFont("Times-Roman", 10)
    pdf.drawRightString(width - 40, height - 35, f"Édité le {now}")
    pdf.setFillColor(colors.black)

    y = height - 80
    y -= 10

    pdf.setFont("Times-Roman", 15)
    texte_intro = (
        f"Dans cette simulation, tu épargnes {epargne_mensuelle:.2f} € par "
        f"mois avec un taux d'intérêt composé de {taux:.1f} %. "
        "Ci-dessous l'évolution de ton épargne dans le temps "
        "et l'impact des intérêts composés."
    )

    pdf.setFont("Times-Roman", 13)

    lines = dessiner_texte_multiligne(
        pdf,
        texte_intro,
        0,
        0,
        width - 100,   # un peu moins large pour joli rendu
        14,
        font_name="Times-Roman",
        font_size=13,
        return_lines=True
    )

    for ligne in lines:
        line_width = pdf.stringWidth(ligne, "Times-Roman", 13)
        x = (width - line_width) / 2
        pdf.drawString(x, y, ligne)
        y -= 14

    y -= 10

    pdf.setFont("Times-Bold", 11)
    pdf.drawString(40, y, "📊 Évolution de ton épargne")
    y -= 10

    # Graphique intérêts composés
    img_buffer = BytesIO()
    fig_composes.savefig(img_buffer, format="png", bbox_inches="tight")
    img_buffer.seek(0)
    pdf.drawImage(ImageReader(img_buffer), 40, y - 200, width=400, height=200)
    y -= 210

    # Tableau 10 ans
    pdf.setFont("Times-Bold", 11)
    pdf.drawString(40, y, "📋 Détail sur 10 ans")
    y -= 20

    # FOND GRIS DU HEADER
    pdf.setFillColor(colors.lightgrey)
    pdf.rect(40, y - 8, width - 200, 18, fill=1, stroke=0)
    pdf.setStrokeColor(colors.black)
    pdf.rect(40, y - 7, width - 200, 18, fill=0, stroke=1)
    pdf.setFillColor(colors.black)

    # En-têtes du tableau
    pdf.setFont("Times-Bold", 10)
    pdf.drawString(40, y, "Année")
    pdf.drawRightString(150, y, "Sans intérêts")
    pdf.drawRightString(280, y, "Avec intérêts")
    pdf.drawRightString(400, y, "Gain")

    y -= 20
    pdf.setFont("Times-Roman", 10)
    row_height = 14
    for row in donnees_tableau:
        pdf.drawString(40, y, f"  {row[0]}")
        pdf.drawRightString(150, y, f"{row[1]}")
        pdf.drawRightString(280, y, f"{row[2]}")
        pdf.drawRightString(400, y, f"{row[3]}")
        y -= row_height
        if y < 60:
            break

    y -= 10
    pdf.line(40, y, width - 40, y)
    y -= 20
    pdf.setFont("Times-Bold", 11)
    pdf.drawString(40, y, "📋 Objectif d'épargne")

    y -= 15
    pdf.setFont("Times-Roman", 10)
    if objectif is not None and epargne_mensuelle > 0:
        mois = int(-(-objectif // epargne_mensuelle))
        texte_obj = (
            f"Avec une épargne mensuelle de {epargne_mensuelle:.2f} €, "
            f"tu atteindras cet objectif de {objectif:.2f} € en environ {mois}"
            f" mois, sans intérêts composés."
        )

        y = dessiner_texte_multiligne(pdf, texte_obj, 40, y, width - 40, 10)
        y -= 1

    # Graphique projection (si disponible)
    if fig_proj is not None:
        img_proj = BytesIO()
        fig_proj.savefig(img_proj, format="png", bbox_inches="tight")
        img_proj.seek(0)
        pdf.drawImage(ImageReader(img_proj),
                      40,
                      y - 180,
                      width=400,
                      height=200)
        y -= 220
    y -= 280
    # -------------------------
    # FOOTER
    # -------------------------
    # Ligne de séparation
    pdf.setStrokeColor(colors.grey)
    pdf.line(40, 55, width - 40, 55)

    # Disclaimer centré visuellement dans la zone
    pdf.setFont("Times-Italic", 7)

    lines = dessiner_texte_multiligne(
        pdf,
        DISCLAIMER,
        0,
        0,
        width - 80,
        8,
        font_name="Times-Italic",
        font_size=7,
        return_lines=True
    )

    y_text = 45

    for ligne in lines:
        line_width = pdf.stringWidth(ligne, "Times-Italic", 7)
        x = (width - line_width) / 2
        pdf.drawString(x, y_text, ligne)
        y_text -= 8

    pdf.save()
    buffer.seek(0)
    return buffer


# ----------------------
# Module Épargne complet
# ----------------------
def module_epargne():
    st.markdown("## 💰 Épargne")
    st.write(
        "Apprends à gérer ton épargne mensuelle et découvre le pouvoir "
        "des intérêts composés."
    )

    st.info(
        "L'épargne est l'acte d'économiser une partie de ses revenus pour "
        "une dépense future, en limitant ses dépenses ou en gérant "
        "prudemment ses ressources financières."
        "\n\nEn France, tu peux utiliser différents produits d'épargne "
        "comme le livret jeune, le Livret A, le Livret d'Épargne Populaire "
        "(LEP), le Livret de Développement Durable et Solidaire (LDDS), le "
        "Plan d'Épargne Logement (PEL), le Compte d'Épargne Logement (CEL) "
        ", .."
        "\n\nPlus de détail sur le site officiel de [La BANQUE DE FRANCE]"
        "(https://www.banque-france.fr/fr/a-votre-service/particuliers/"
        "connaitre-pratiques-bancaires-assurance/epargne)."
    )

    if "budget_data" not in st.session_state:
        st.info("Analyse d'abord ton budget dans le module Budget.")
        st.session_state.budget_data = {
            "revenu": 0.0,
            "depenses": {},
            "reste": 0.0
        }
        return

    budget = st.session_state.budget_data
    reste = budget.get("reste", 0)
    depenses = sum(budget.get("depenses", {}).values())

    # Épargne de précaution
    st.markdown("### 🛟 Épargne de précaution")
    st.write(
        "L'épargne de précaution correspond à l'argent mis de côté "
        "pour faire face aux imprévus (maladie, panne, perte d'emploi). "
        "\nIl est recommandé de mettre de côté 3 à 6 mois de dépenses."
        f"\n\nDans ton cas, avec des dépenses mensuelles de {depenses:.2f} €,"
        " tu devrais viser :"
    )
    epargne_min = depenses * 3
    epargne_ideal = depenses * 6
    col1, col2 = st.columns(2)
    col1.metric("Objectif minimum (3 mois)", f"{epargne_min:,.0f} €")
    col2.metric("Objectif idéal (6 mois)", f"{epargne_ideal:,.0f} €")

    # Simulation épargne
    st.markdown("---")
    st.markdown("### 💵 Simulation d'épargne - Intérêts Composés")
    st.write(
        "Les intérêts composés sont un mécanisme financier où les intérêts "
        "générés s'ajoutent au capital initial et produisent eux-mêmes des "
        "intérêts lors des périodes suivantes, amplifiant ainsi la "
        "croissance exponentielle des rendements."
    )

    if reste <= 0:
        st.warning(
            "Ton reste mensuel est nul ou négatif. "
            "Ajuste ton budget pour pouvoir épargner."
        )
        return

    st.info(
        "Les taux utilisés ici sont indicatifs. En France, les livrets "
        "réglementés (Livret A, LEP...) ont des taux fixés par l'État."
    )

    epargne = st.slider(
        "Combien souhaites-tu épargner chaque mois ?",
        0.0,
        float(max(reste, 0)),
        float(max(reste * 0.2, 0))
    )
    taux = st.slider(
        "Taux d'intérêt composé annuel (%)",
        0.0,
        10.0,
        3.0,
        step=0.1
    )

    # Graphique intérêts composés et tableau
    fig_composes, annees, capital_simple, capital_composes = \
        creer_graphique_interets_composes(epargne, taux)
    gains = [comp - sim for comp, sim in zip(capital_composes, capital_simple)]

    tableau_df = pd.DataFrame({
        "Année": annees,
        " Sans intérêts (€)": [
            f"{val:,.0f} €".replace(",", " ") for val in capital_simple
        ],
        " Avec intérêts (€)": [
            f"{val:,.0f} €".replace(",", " ") for val in capital_composes
        ],
        " Gain (€)": [f"{val:,.0f} €".replace(",", " ") for val in gains]
    })

    st.pyplot(fig_composes)
    st.markdown("### 📊 Évolution sur 10 ans")
    st.table(tableau_df.to_dict("records"))

    # Metrics
    st.markdown("### 💡 Capital et intérêts")
    col1, col2 = st.columns(2)
    col1.metric("Capital investi",
                f"{capital_simple[-1]:,.0f} €".replace(",", " "))
    col2.metric("Intérêts gagnés", f"{gains[-1]:,.0f} €".replace(",", " "))

    # Projection vers objectif
    st.markdown("---")
    st.markdown("### 🎯 Objectif d'épargne")
    objectif_input = st.text_input("Par défaut, l'objectif est de 1 000 €. "
                                   "Mets le montant souhaité :", value="1000")
    try:
        objectif = float(objectif_input.replace(",", "."))
        if objectif < 1:
            objectif = None
    except ValueError:
        objectif = None

    fig_proj = None
    if objectif and epargne > 0:
        mois = int(-(-objectif // epargne))
        st.success(f"À ce rythme de {epargne:.2f} € d'épargne mensuelle, il "
                   f"faudrait ≈ {mois} mois pour atteindre {objectif:.2f} €.")
        cumul = [epargne * m for m in range(1, mois+1)]
        fig_proj, ax = plt.subplots()
        ax.plot(range(1, mois+1), cumul, marker="o", color="#2563EB")
        ax.axhline(y=objectif, color="r", linestyle="--", label="Objectif")
        ax.set_xlabel("Mois")
        ax.set_ylabel("Épargne cumulée (€)")
        ax.set_title("Projection d'épargne")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig_proj)

    st.info(
        "Pour composer son épargne de précaution ou pour la réalisation "
        "d'un objectif à court terme (environ 1 an), il est généralement "
        "recommandé de privilégier des produits d'épargne sécurisés et "
        "liquides (retrait facile) comme le livret jeune, le LEP ou le Livret "
        "A. \n\nLes intérêts composés permettent à ton argent de croître "
        "plus rapidement grâce à l'accumulation des intérêts sur les "
        "intérêts déjà gagnés."
        "\n\nPlus de détail sur le site officiel de [La BANQUE DE FRANCE]"
        "(https://www.banque-france.fr/fr/a-votre-service/particuliers/"
        "connaitre-pratiques-bancaires-assurance/epargne)."
    )

    # PDF
    pdf = generer_pdf_epargne(
        epargne, taux, fig_composes, tableau_df.values.tolist(),
        objectif=objectif, fig_proj=fig_proj
    )
    st.download_button(
        "📄 Télécharger le rapport épargne",
        pdf,
        "rapport_epargne.pdf",
        "application/pdf"
    )

    plt.close(fig_composes)
    if fig_proj:
        plt.close(fig_proj)

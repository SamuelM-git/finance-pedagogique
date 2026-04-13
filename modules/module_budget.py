import streamlit as st
import matplotlib.pyplot as plt
import unicodedata
import math
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from progress import valider_etape


# ========================
# Constantes
# ========================
PLATFORM_NAME = "Finance LudiK"
DISCLAIMER = (
    "Les informations et outils proposés ont une finalité exclusivement"
    " pédagogique et informative. Les données saisies sont traitées"
    " temporairement, sans stockage. Les résultats fournis sont des"
    " simulations indicatives et ne constituent pas un conseil financier"
    " personnalisé ni un service de conseil en investissement."
    " L'utilisateur reste seul responsable des décisions prises sur"
    " cette base."
)

CATEGORIES = [
    "Loyer", "Courses", "Transports", "Loisirs",
    "Abonnement téléphonique", "Abonnement Internet",
    "Autres abonnements", "Autres"
]

CHARGES_FIXES = ["Loyer", "Abonnement téléphonique", "Abonnement Internet",
                 "Autres abonnements"]
CHARGES_VARIABLES = ["Courses", "Transports", "Loisirs", "Autres"]


# ========================
# Fonctions utilitaires
# ========================
def normaliser_cle(texte: str) -> str:
    """Normalise une clé pour session_state"""
    texte = unicodedata.normalize("NFKD", texte)
    texte = texte.encode("ascii", "ignore").decode("ascii")
    return texte.replace(" ", "_").lower()


# ------------------------
# Calculs budget
# ------------------------
def calculer_budget(revenu: float, depenses: dict) -> tuple:
    total_dep = sum(depenses.values())
    reste = revenu - total_dep
    taux_depense = (total_dep / revenu * 100) if revenu > 0 else 0
    total_fixes = sum(depenses.get(cat, 0) for cat in CHARGES_FIXES)
    total_variables = sum(depenses.get(cat, 0) for cat in CHARGES_VARIABLES)
    return total_dep, reste, taux_depense, total_fixes, total_variables


def evaluer_situation_budget(revenu: float, depenses: dict,
                             reste: float) -> dict:
    if revenu <= 0:
        return {"niveau": "indetermine", "message": "Revenu non renseigné.",
                "score": 0}
    taux_epargne = reste / revenu
    if reste < 0:
        return {"niveau": "critique", "message": "Situation déficitaire.",
                "score": 0}
    if taux_epargne < 0.1:
        return {"niveau": "fragile", "message": "Marge d'épargne faible.",
                "score": 40}
    if taux_epargne < 0.2:
        return {"niveau": "stable", "message": "Situation saine.", "score": 70}
    return {"niveau": "excellente",
            "message": "Excellente gestion budgétaire.", "score": 100}


def generer_conseils(depenses: dict) -> str:
    conseils = []
    for cat, val in sorted(depenses.items(), key=lambda x: x[1], reverse=True):
        if val <= 0:
            continue
        msg = f"{cat} : {val:.2f} € — "
        if cat == "Loyer":
            msg += (
                "Tu peux vérifier ton éligibilité aux aides au logement."
            )
        elif cat == "Courses":
            msg += (
                "Tu peux peut-être comparer les prix et planifier tes "
                "achats."
            )
        elif cat == "Transports":
            msg += (
                "Si possible, privilégier les transports en commun, vélo "
                "ou covoiturage. Tu peux aussi vérifier les aides à la "
                "mobilité."
            )
        elif cat in ["Loisirs", "Autres"]:
            msg += (
                "Si possible, tu peux essayer de les réduire, même "
                "légèrement, afin d'améliorer ta capacité d'épargne."
            )
        elif cat == "Abonnement téléphonique":
            msg += (
                "Tu peux peut-être comparer les offres et réduire "
                "les options inutiles."
            )
        elif cat == "Abonnement Internet":
            msg += (
                "Si possible, essai de vérifier si ton offre est "
                "adaptée à ton usage."
            )
        elif cat == "Autres abonnements":
            msg += (
                "Si possible, prend le temps de répertorier tes "
                "abonnements et supprimez ceux non utilisés."
            )
        conseils.append("• " + msg)
    return "\n\n".join(conseils)


def couper_texte_par_lignes(texte, max_lignes=8):
    lignes = texte.split("•")
    if len(lignes) <= max_lignes:
        return texte + "\n"
    return "\n".join(lignes[:max_lignes]) + "\n..."


# ------------------------
# Graphiques
# ------------------------
def creer_graphique_depenses(depenses: dict) -> plt.Figure:
    data = {k: v for k, v in depenses.items() if v > 0}
    fig, ax = plt.subplots(figsize=(8, 4))
    if data:
        colors_list = ["#22C55E" if k in CHARGES_VARIABLES else "#2563EB"
                       for k in data.keys()]
        ax.barh(list(data.keys()), list(data.values()), color=colors_list)
        ax.invert_yaxis()
    plt.tight_layout()
    return fig


def creer_graphique_fixes_variables(total_fixes: float,
                                    total_variables: float) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie([total_fixes, total_variables], labels=["Charges fixes",
                                                   "Charges variables"],
           autopct="%1.1f%%", colors=["#2563EB", "#22C55E"])
    plt.tight_layout()
    return fig


def creer_graphique_503020(revenu: float, depenses: dict,
                           reste: float) -> plt.Figure:
    necessaire = (depenses.get("Loyer", 0)
                  + depenses.get("Courses", 0)
                  + depenses.get("Transports", 0))
    loisirs = depenses.get("Loisirs", 0)
    epargne = max(reste, 0)
    reel = [necessaire, loisirs, epargne]
    ideal = [revenu * 0.5, revenu * 0.3, revenu * 0.2]
    labels = ["Besoins", "Loisirs", "Épargne"]
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x, reel, width=0.4, label="Réel")
    ax.bar([i + 0.4 for i in x], ideal, width=0.4, label="Idéal")
    ax.set_xticks([i + 0.2 for i in x])
    ax.set_xticklabels(labels)
    ax.legend()
    plt.tight_layout()
    return fig


# ------------------------
# PDF
# ------------------------
def dessiner_texte_multiligne(
    pdf,
    texte,
    x,
    y,
    max_width,
    line_height=10,
    font_name="Times-Roman",
    font_size=10,
    return_lines=False
):
    paragraphes = texte.split("\n")
    lignes = []

    for paragraphe in paragraphes:
        mots = paragraphe.split()
        ligne_courante = ""

        for mot in mots:
            test = ligne_courante + " " + mot if ligne_courante else mot
            if pdf.stringWidth(test, font_name, font_size) < max_width:
                ligne_courante = test
            else:
                lignes.append(ligne_courante)
                ligne_courante = mot

        if ligne_courante:
            lignes.append(ligne_courante)

        if paragraphe.strip():
            lignes.append("")

    if return_lines:
        return lignes

    for ligne in lignes:
        pdf.drawString(x, y, ligne)
        y -= line_height

    return y


def generer_pdf_budget(revenu, depenses, reste, taux_depense, diagnostic,
                       conseils, fig_categorie, fig_503020,
                       fig_fixes_variables):

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # -------------------------
    # HEADER
    # -------------------------
    pdf.setFillColor(colors.HexColor("#2563EB"))
    pdf.rect(0, height - 60, width, 60, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 16)
    pdf.drawString(40, height - 32, "Finance LudiK — Le module budget")
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(40, height - 48, "Par Samuel M, Data Analyst pour aider à"
                                    " la décision")

    pdf.setFont("Times-Roman", 10)
    pdf.drawRightString(width - 40, height - 35, f"Édité le {now}")

    pdf.setFillColor(colors.black)

    y = height - 80

    # -------------------------
    # SCORE VISUEL
    # -------------------------
    score = diagnostic["score"]
    taux_epargne = reste / revenu if revenu > 0 else 0

    color = (
              "#22C55E"
              if score >= 70
              else "#F59E0B" if score >= 40
              else "#EF4444"
        )

    pdf.setFillColor(colors.HexColor(color))
    pdf.roundRect(40, y - 30, 145, 25, 8, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Times-Bold", 12)
    pdf.drawCentredString(
        100,
        y - 22,
        f"       Taux d'épargne : {taux_epargne:.1%}"
    )
    pdf.setFillColor(colors.black)

    # -------------------------
    # RÉSUMÉ (encadré)
    # -------------------------
    y -= 50

    pdf.setStrokeColor(colors.grey)
    pdf.rect(40, y - 70, width - 80, 60)

    pdf.setFont("Times-Bold", 11)
    pdf.drawString(50, y - 8, "Résumé")

    pdf.setFont("Times-Roman", 10)
    pdf.drawString(50, y - 25, f"Revenu mensuel : {revenu:.2f} €")
    pdf.drawString(50, y - 40, f"Dépenses totales : "
                               f"{sum(depenses.values()):.2f} €")
    pdf.drawString(50, y - 55, f"Reste mensuel : {reste:.2f} €")
    pdf.drawString(250, y - 25, f"Taux de dépense : {taux_depense:.1f} %")
    pdf.drawString(250, y - 40, f"Taux d'épargne : {taux_epargne:.1%} ")

    # -------------------------
    # GRAPHIQUES STRUCTURÉS
    # -------------------------

    def bloc_graphique(titre, description, fig, x, y):
        # Fond léger
        pdf.setFillColor(colors.whitesmoke)
        pdf.roundRect(x - 5, y - 135, 200, 135, 8, fill=1, stroke=0)

        pdf.setFillColor(colors.black)

        # Titre
        pdf.setFont("Times-Bold", 10)
        pdf.drawString(x, y, titre)

        # Description
        pdf.setFont("Times-Roman", 8)
        dessiner_texte_multiligne(pdf, description, x, y - 12, 240)

        # Graphique
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png", bbox_inches="tight")
        img_buffer.seek(0)

        pdf.drawImage(
            ImageReader(img_buffer),
            x,
            y - 125,
            width=180,
            height=110
        )

    y -= 135

    # Ligne 1 : 2 graphiques côte à côte
    bloc_graphique(
        "Répartition des dépenses",
        "Regarde où part ton argent pour mieux gérer ton budget.",
        fig_categorie,
        40,
        y
    )

    bloc_graphique(
        "Charges fixes vs variables",
        "Visualise la répartition de tes charges par type.",
        fig_fixes_variables,
        width / 2 + 10,
        y
    )

    # Ligne 2 : centré
    y -= 160

    bloc_graphique(
        "Règle 50 / 30 / 20",
        "Compare ton budget réel avec une répartition idéale.",
        fig_503020,
        width / 2 - 110,
        y
    )

    # -------------------------
    # CONSEILS (encadré)
    # -------------------------
    y -= 160

    pdf.setStrokeColor(colors.grey)

    # Fond
    pdf.setFillColor(colors.whitesmoke)
    pdf.rect(40, y - 175, width - 80, 175, fill=1, stroke=0)

    # Bordure
    pdf.setStrokeColor(colors.grey)
    pdf.rect(40, y - 175, width - 80, 175, fill=0)

    # Titre
    pdf.setFont("Times-Bold", 11)
    pdf.setFillColor(colors.black)
    pdf.drawString(50, y - 15, "Des suggestions pour améliorer ton budget :")

    # Texte multiligne
    pdf.setFont("Times-Roman", 8)
    pdf.setFillColor(colors.black)
    dessiner_texte_multiligne(
        pdf,
        conseils,
        x=50,
        y=y - 35,      # position sous le titre
        max_width=width - 80,   # largeur du bloc moins les marges
        line_height=9   # hauteur de ligne
    )

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


# ========================
# Module Streamlit
# ========================
def module_budget():

    if "etapes" not in st.session_state:
        st.session_state.etapes = {}

    # ========================
    # On s'assure que les données de budget sont initialisées dans
    # session_state
    # ========================
    if "budget_data" not in st.session_state:
        st.session_state.budget_data = {
            "revenu": 0.0,
            "depenses": {cat: 0.0 for cat in CATEGORIES}
        }

    st.markdown(
        """
        <h2 style='color:#2563EB;'>💸 Analyse de Budget</h2>
        """,
        unsafe_allow_html=True
    )
    st.info("Renseigne tes revenus et dépenses puis analyse ton budget."
            " La règle 50/30/20 t'aide à répartir tes dépenses.")

    revenu = st.number_input(
        "💵 Revenu mensuel (€)",
        min_value=0.0,
        step=100.0,
        value=float(st.session_state.budget_data.get("revenu", 0.0)),
    )
    st.session_state.budget_data["revenu"] = revenu

    if revenu <= 0:
        st.warning("Veuillez renseigner un revenu valide avant d'analyser.")
        return

    depenses = {}
    for cat in CATEGORIES:
        val = st.number_input(
            f"{cat} (€)",
            min_value=0.0,
            step=10.0,
            value=float(
                st.session_state.budget_data["depenses"].get(cat, 0.0)
            ),
            key=f"dep_{normaliser_cle(cat)}"
        )

        if val is None or math.isnan(val):
            val = 0.0
        depenses[cat] = float(val)

    st.session_state.budget_data["depenses"] = depenses

    if all(val == 0 for val in depenses.values()):
        st.info("💡 Ajoutez au moins une dépense pour obtenir une analyse.")

    if st.button("📊 Analyser mon budget"):

        if all(val == 0 for val in depenses.values()):
            st.error("Veuillez renseigner au moins une dépense avant "
                     "d'analyser votre budget.")
            return

        (total_dep,
         reste,
         taux_depense,
         total_fixes,
         total_variables) = calculer_budget(revenu, depenses)
        diagnostic = evaluer_situation_budget(revenu, depenses, reste)
        conseils = generer_conseils(depenses)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Dépenses totales", f"{total_dep:.2f} €")
        col2.metric("Reste mensuel", f"{reste:.2f} €")
        col3.metric("Taux de dépense", f"{taux_depense:.1f} %")
        col4.metric("Taux d'épargne", f"{max(reste / revenu * 100, 0):.1f} %")
        if reste < 0:
            st.error("⚠️ Attention : votre budget est déficitaire !")
        st.info(diagnostic["message"])

        fig_categorie = creer_graphique_depenses(depenses)
        fig_503020 = creer_graphique_503020(revenu, depenses, reste)
        fig_fixes_variables = creer_graphique_fixes_variables(total_fixes,
                                                              total_variables)

        st.markdown("### 📊 Répartition des dépenses par catégorie")
        st.info(
            "Ce n'est pas facile de réduire ses dépenses, mais comprendre "
            "où va son argent est essentiel pour mieux le gérer."
        )
        st.pyplot(fig_categorie)
        st.markdown(conseils)
        st.markdown("### 📊 Répartition charges fixes / variables")
        st.info(
            "Dans les charges fixes, on trouve les dépenses régulières et "
            "incontournables comme le loyer et les abonnements. Alors que "
            "les charges variables sont plus flexibles et peuvent être "
            "ajustées plus ou moins facilement en fonction de tes choix et "
            "de ta situation. Ce sont par exemple les courses, les "
            "transports ou les loisirs. "
        )
        st.pyplot(fig_fixes_variables)
        st.markdown("### 📊 Règle 50 / 30 / 20")
        st.info(
            "La règle 50/30/20 est une méthode de gestion budgétaire qui "
            "recommande de répartir ses dépenses en trois catégories : "
            "50 % pour les besoins, 30 % pour les loisirs et 20 % pour "
            "l'épargne. \n\nCette règle a été développée en 2005 "
            "par la sénatrice américaine Elisabeth Warren dans un guide "
            "pratique de gestion budgétaire.\n\nSource : [www.lafinancepour"
            "tous.com](https://www.lafinancepourtous.com/outils/questions-r"
            "eponses/budget-qu-est-ce-que-la-regle-des-50-30-20/)."
        )

        st.pyplot(fig_503020)

        st.session_state.budget_data = {
            "revenu": revenu,
            "depenses": depenses,
            "reste": reste,
            "taux": taux_depense,
            "diagnostic": diagnostic
        }

        pdf_buffer = generer_pdf_budget(revenu, depenses, reste, taux_depense,
                                        diagnostic, conseils, fig_categorie,
                                        fig_503020, fig_fixes_variables)
        st.download_button("📥 Télécharger le rapport PDF", pdf_buffer,
                           "rapport_budget.pdf", "application/pdf")

        plt.close(fig_categorie)
        plt.close(fig_503020)
        plt.close(fig_fixes_variables)

        if not st.session_state.etapes.get("budget", False):
            valider_etape("budget", xp=20, badge="📊 Budget analysé")
            st.success("🔥 +20 XP — Badge débloqué : Budget analysé")

    st.markdown("---")

    if st.button("🗑️ Effacer les données"):
        st.session_state.budget_data = {
            "revenu": 0.0,
            "depenses": {cat: 0.0 for cat in CATEGORIES}
        }
        for cat in CATEGORIES:
            key = f"dep_{normaliser_cle(cat)}"
            if key in st.session_state:
                del st.session_state[key]

        st.success("Les données ont été effacées.")
        st.rerun()

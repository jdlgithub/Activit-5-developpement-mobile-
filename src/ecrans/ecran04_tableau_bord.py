"""Ecran 4 — Tableau de bord / fil d'actualite.

Objectif : montrer le materiel disponible a l'emprunt sur le campus.

Elements requis satisfaits : header avec logo, barre de recherche et icone de
notifications ; barre de filtres horizontaux par categorie ; grille de cartes
(visuel, titre, etat, proprietaire) ; navigation inferieure (Accueil,
Publier, Messages, Profil).
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    barre_etat,
    barre_onglets,
    barre_recherche,
    carte_objet,
    hauteur_ligne,
    icone_cloche,
    logo,
    rangee_puces,
)
from ..donnees import CATEGORIES, OBJETS
from ..scene import H_DROITE, Ecran, Ellipse, Texte

NOM = "04 · Tableau de bord"

# Grille 2 colonnes.
COLONNE = (UTILE - charte.ESP_3) / 2
HAUTEUR_CARTE = 190
GOUTTIERE = charte.ESP_3


def construire() -> Ecran:
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 4 — Tableau de bord. Header (logo, recherche, notifications), "
            "filtres par categorie, grille de cartes objet, barre d'onglets."
        ),
    )

    ecran.ajouter(*barre_etat())

    # --- Header : logo + nom a gauche, notification a droite ---
    y = 34
    ecran.ajouter(*logo(M + 15, y + 18, 30))
    ecran.ajouter(Texte(M + 38, y + 8, 160, "CampusShare", 17, True, charte.TEXTE))
    ecran.ajouter(
        Texte(M + 38, y + 31, 180, "Bâtiment A · Bibliothèque", 10, False, charte.TEXTE_DISCRET)
    )

    # Notifications : pastille de non-readue, cible tactile 44 px.
    cx_notif = LARGEUR - M - 22
    ecran.ajouter(*icone_cloche(cx_notif, y + 18, charte.TEXTE))
    ecran.ajouter(Ellipse(cx_notif + 9, y + 6, 9, 9, charte.ALERTE, "#FFFFFF", 1.5))

    y += 52

    # --- Barre de recherche ---
    ecran.ajouter(*barre_recherche(M, y, UTILE))
    y += 42 + charte.ESP_3

    # --- Filtres horizontaux par categorie ---
    # Seules les puces tenant dans la largeur utile sont dessinees : la maquette
    # ne presente aucun element hors cadre. Les suivantes sont accessibles par
    # defilement horizontal.
    puces, largeur_puces, tronquee = rangee_puces(M, y, UTILE, CATEGORIES, actif=0, ecran=charte.ESP_2)
    ecran.ajouter(*puces)
    if tronquee:
        ecran.ajouter(
            Texte(M + largeur_puces + charte.ESP_1, y + 8, 60, "…", charte.T_LABEL, True, charte.TEXTE_DISCRET)
        )
    y += 32 + charte.ESP_4

    # --- Titre de section ---
    ecran.ajouter(
        Texte(M, y, UTILE * 0.7, "Disponible près de vous", charte.T_TITRE_SECTION, True, charte.TEXTE)
    )
    ecran.ajouter(
        Texte(M + UTILE * 0.7, y + 3, UTILE * 0.3, "%d objets" % len(OBJETS),
              charte.T_LABEL, False, charte.TEXTE_SECONDAIRE, H_DROITE)
    )
    y += hauteur_ligne(charte.T_TITRE_SECTION) + charte.ESP_4

    # --- Grille de cartes ---
    for i, objet in enumerate(OBJETS[:4]):
        colonne = i % 2
        ligne = i // 2
        ecran.ajouter(
            *carte_objet(M + colonne * (COLONNE + GOUTTIERE),
                         y + ligne * (HAUTEUR_CARTE + GOUTTIERE),
                         COLONNE, objet, HAUTEUR_CARTE)
        )

    # --- Navigation inferieure ---
    ecran.ajouter(*barre_onglets(actif="accueil"))

    return ecran
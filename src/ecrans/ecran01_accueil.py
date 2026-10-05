"""Ecran 1 — Splash screen / Accueil (bienvenue).

Premier ecran au lancement. Objectif :Presenter la promesse de l'application
et proposer deux entrees : connexion ou creation de compte.

Composition : fond vert plein (couleur primaire), logo centre, slogan, puis les
deux boutons ancres en bas. Aucun contenu superflu au premier lancement.
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    barre_etat,
    logo_clair,
)
from ..scene import H_CENTRE, Ecran, Forme, Texte

NOM = "01 · Accueil / Bienvenue"


def construire() -> Ecran:
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.VERT,
        note=(
            "Ecran 1 — Splash / Accueil. Logo, slogan et deux entrees : "
            "connexion et creation de compte."
        ),
    )

    # La barre d'etat systeme est en clair sur fond vert.
    ecran.ajouter(*barre_etat(couleur="#FFFFFF"))

    # --- Bloc de marque, centre dans la moitie haute ---
    centre_x = LARGEUR / 2
    y_logo = 236
    ecran.ajouter(*logo_clair(centre_x, y_logo, 76))
    ecran.ajouter(
        Texte(0, y_logo + 62, LARGEUR, "CampusShare", 26, True, "#FFFFFF", H_CENTRE)
    )

    # Slogan : deux lignes courtes, forte lisibilite.
    ecran.ajouter(
        Texte(
            M, y_logo + 106, UTILE,
            "Le partage de matériel<br>entre étudiants",
            15, False, "#D8EBD9", H_CENTRE, hauteur=15 * 1.35 * 2,
        )
    )

    # --- Bloc de preuve de confiance, discret ---
    y_badges = y_logo + 176
    ecran.ajouter(
        Forme(M, y_badges, UTILE, 64, "#276B2B", 12, None, 0, nom="Bannière / réassurance")
    )
    ecran.ajouter(
        Texte(
            M + 16, y_badges + 10, UTILE - 32,
            "Un campus, moins de gaspillage.<br>"
            "Empruntez ce dont vous avez besoin, rendez-le en bon état.",
            12, False, "#CBE3CD", interligne=1.35,
        )
    )

    # --- Actions principales, ancrees en bas ---
    y_bas = HAUTEUR - 40 - 2 * charte.BOUTON_H - charte.ESP_3

    # Sur fond vert, l'action principale est blanche ; l'action secondaire
    # reste un contour blanc (un seul niveau d'emphase).
    ecran.ajouter(
        Forme(
            M, y_bas, UTILE, charte.BOUTON_H, "#FFFFFF", charte.RAYON_BOUTON,
            None, 0, nom="Bouton / Se connecter",
        ),
        Texte(
            M, y_bas + (charte.BOUTON_H - 15 * 1.3) / 2, UTILE,
            "Se connecter", charte.T_BOUTON, True, charte.VERT, H_CENTRE,
        ),
    )

    y_second = y_bas + charte.BOUTON_H + charte.ESP_3
    ecran.ajouter(
        Forme(
            M, y_second, UTILE, charte.BOUTON_H, None, charte.RAYON_BOUTON,
            "#FFFFFF", 1, nom="Bouton / Créer un compte",
        ),
        Texte(
            M, y_second + (charte.BOUTON_H - 15 * 1.3) / 2, UTILE,
            "Créer un compte", charte.T_BOUTON, True, "#FFFFFF", H_CENTRE,
        ),
    )

    ecran.ajouter(
        Texte(
            0, HAUTEUR - 30, LARGEUR,
            "Réservé aux étudiants du campus", 11, False, "#B6D2B9", H_CENTRE,
        )
    )

    return ecran
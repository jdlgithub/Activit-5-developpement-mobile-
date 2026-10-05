"""Ecran 7 — Publication d'un objet (ajout de materiel).

Objectif : permettre a un etudiant de proposer son materiel au pret.

Elements requis satisfaits : nom de l'objet, categorie, ajout de photo
(placeholder), description et conditions, bouton « Publier l'annonce ».
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    barre_action_fixe,
    barre_etat,
    bouton,
    champ,
    champ_selecteur,
    hauteur_champ,
    hauteur_ligne,
    icone_camera,
    icone_coche,
    icone_retour,
    puce_filtre,
    zone_texte,
)
from ..donnees import CATEGORIES
from ..scene import H_CENTRE, Ecran, Forme, Texte

NOM = "07 · Publication d'un objet"

# Zone d'ajout de photos : hauteur du placeholder.
ZONE_PHOTO_H = 124
HAUTEUR_DESCRIPTION = 88
HAUTEUR_CONDITIONS = 72

# Categories excluant « Tous ».
CATEGORIE_PUBLIABLE = [c for c in CATEGORIES if c != "Tous"]


def construire() -> Ecran:
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 7 — Publication d'un objet. Ajout de photo (placeholder), "
            "nom, categorie, description, conditions, bouton « Publier "
            "l'annonce »."
        ),
    )

    ecran.ajouter(*barre_etat())

    # --- Barre superieure ---
    y = 34
    ecran.ajouter(*icone_retour(M + 11, y + 22, charte.TEXTE))
    ecran.ajouter(
        Texte(0, y + 14, LARGEUR, "Publier un objet", charte.T_SOUS_TITRE, True, charte.TEXTE,
              align_h=1)
    )
    y += 58

    # --- Titre d'accroche ---
    ecran.ajouter(
        Texte(
            M, y, UTILE,
            "Partagez ce que vous n'utilisez pas.",
            17, True, charte.TEXTE,
        )
    )
    y += hauteur_ligne(17) + charte.ESP_4

    # --- Ajout de photos (placeholder) ---
    ecran.ajouter(
        Forme(M, y, UTILE, ZONE_PHOTO_H, charte.SURFACE, charte.RAYON_CARTE,
              charte.BORDURE_FORCE, 1, style_bordure="dashed", nom="Photos / placeholder"),
        *icone_camera(M + UTILE / 2, y + 38, charte.VERT, 30),
        Texte(M, y + 70, UTILE, "Ajouter des photos", 13, True, charte.VERT, H_CENTRE),
        Texte(M, y + 92, UTILE, "3 photos maximum · JPG ou PNG", 11, False,
              charte.TEXTE_DISCRET, H_CENTRE),
    )
    y += ZONE_PHOTO_H + charte.ESP_4

    # --- Nom de l'objet ---
    ecran.ajouter(*champ(M, y, UTILE, "Nom de l'objet", "Ex. Perceuse à percussion Bosch"))
    y += hauteur_champ(True) + charte.ESP_3

    # --- Categorie ---
    ecran.ajouter(*champ_selecteur(M, y, UTILE, "Catégorie", CATEGORIE_PUBLIABLE[1]))
    y += hauteur_champ(True) + charte.ESP_3

    # --- Description et conditions ---
    ecran.ajouter(
        *zone_texte(
            M, y, UTILE, "Description",
            "État, puissance, accessoires fournis…<br>"
            "Soyez précis : cela rassure les emprunteurs.",
            h=HAUTEUR_DESCRIPTION,
        )
    )
    y += hauteur_champ(False) + HAUTEUR_DESCRIPTION + charte.ESP_3

    ecran.ajouter(
        *zone_texte(
            M, y, UTILE, "Conditions de prêt",
            "Ex. Restitution dans le local du département, 5 jours maximum.",
            h=HAUTEUR_CONDITIONS,
        )
    )
    y += hauteur_champ(False) + HAUTEUR_CONDITIONS + charte.ESP_3

    # --- Engagement de restitution ---
    ecran.ajouter(*icone_coche(M + 6, y + 7, charte.VERT, 14))
    ecran.ajouter(
        Texte(
            M + 22, y, UTILE - 22,
            "Je m'engage à prendre soin de l'objet et à le prêter<br>"
            "dans le respect de la charte CampusShare.",
            11, False, charte.TEXTE_SECONDAIRE, interligne=1.25,
        )
    )

    # --- Action fixe ---
    y_action = HAUTEUR - charte.BARRE_ACTION
    ecran.ajouter(
        *barre_action_fixe(y_action, [bouton(M, y_action + 14, UTILE, "Publier l'annonce")])
    )

    return ecran
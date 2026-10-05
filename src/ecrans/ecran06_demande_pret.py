"""Ecran 6 — Formulaire de demande de pret.

Objectif : soumettre une demande d'emprunt au proprietaire.

Elements requis satisfaits : selecteurs de date (debut / fin), zone de texte
pour un message au proprietaire, rappel des regles de restitution
eco-responsables, bouton de validation « Envoyer la demande ».
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
    champ_selecteur,
    hauteur_champ,
    hauteur_ligne,
    icone_agenda,
    icone_coche,
    icone_retour,
    message_info,
    vignette,
    visuel,
    zone_texte,
)
from ..donnees import DUREES, trouver
from ..scene import Ecran, Forme, Texte

NOM = "06 · Demande de prêt"

OBJET = trouver("Projecteur Epson EB-2150")

# Hauteur de la zone de message libre.
HAUTEUR_MESSAGE = 96


def construire() -> Ecran:
    objet = OBJET
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 6 — Formulaire de demande de pret. Selecteurs de date "
            "(debut/fin), message au proprietaire, rappel des regles de "
            "restitution, bouton « Envoyer la demande »."
        ),
    )

    ecran.ajouter(*barre_etat())

    # --- Barre superieure ---
    y = 34
    ecran.ajouter(*icone_retour(M + 11, y + 22, charte.TEXTE))
    ecran.ajouter(
        Texte(0, y + 14, LARGEUR, "Demande de prêt", charte.T_SOUS_TITRE, True, charte.TEXTE,
              align_h=1)
    )
    y += 58

    # --- Rappel de l'objet demande ---
    hauteur_rappel = 74
    ecran.ajouter(Forme(M, y, UTILE, hauteur_rappel, charte.SURFACE, charte.RAYON_CARTE,
                        charte.BORDURE, 1, nom="Carte / objet demandé"))
    ecran.ajouter(*vignette(M + 10, y + 10, 54, 54, charte.VIGNETTE, visuel(objet.categorie)))
    ecran.ajouter(
        Texte(M + 74, y + 14, UTILE - 84, objet.titre, charte.T_CORPS_FORT, True, charte.TEXTE,
              hauteur=hauteur_ligne(14, 1.25) * 2)
    )
    ecran.ajouter(
        Texte(M + 74, y + 44, UTILE - 84, "à %s" % objet.proprietaire.nom, 11, False,
              charte.TEXTE_DISCRET)
    )
    y += hauteur_rappel + charte.ESP_5

    # --- Periode de pret : deux colonnes ---
    colonne = (UTILE - charte.ESP_3) / 2
    ecran.ajouter(*champ_selecteur(M, y, colonne, "Du", "12 nov. 2025", icone=icone_agenda))
    ecran.ajouter(*champ_selecteur(M + colonne + charte.ESP_3, y, colonne, "Au", "17 nov. 2025",
                               icone=icone_agenda))
    y += hauteur_champ(True) + charte.ESP_2

    # Duree resultante : information calculee, mise en avant en orange doux.
    ecran.ajouter(
        *message_info(
            M, y, UTILE,
            "Durée de l'emprunt : <b>%s</b> — conforme à la limite proposée par %s."
            % (DUREES[2], objet.proprietaire.nom),
            charte.VERT_CLAIR, charte.VERT_CLAIR, charte.VERT, icone_coche,
        )
    )
    y += 52 + charte.ESP_5

    # --- Message au proprietaire ---
    ecran.ajouter(
        *zone_texte(
            M, y, UTILE, "Message au propriétaire",
            "Bonjour %s,<br>Je présenterais le projet de fin d'études mardi. "
            "Serait-il possible de récupérer le projecteur en fin de journée ?"
            % objet.proprietaire.nom.split()[0],
            h=HAUTEUR_MESSAGE,
        )
    )
    y += hauteur_champ(False) + HAUTEUR_MESSAGE + charte.ESP_4

    # --- Regles eco-responsables ---
    ecran.ajouter(
        Texte(M, y, UTILE, "Règles de restitution", charte.T_SOUS_TITRE, True, charte.TEXTE)
    )
    y += hauteur_ligne(charte.T_SOUS_TITRE) + charte.ESP_3

    for regle in (
        "Restituer à la date convenue, ou prévenir le propriétaire.",
        "Rapporter l'objet propre et complet, accessories inclus.",
        "Signaler tout dégât plutôt que de le dissimuler.",
    ):
        ecran.ajouter(*icone_coche(M + 6, y + 7, charte.VERT, 14))
        ecran.ajouter(
            Texte(M + 22, y, UTILE - 22, regle, 11, False, charte.TEXTE_SECONDAIRE,
                  hauteur=hauteur_ligne(11, 1.35))
        )
        y += hauteur_ligne(11, 1.35) + 4

    # --- Action fixe ---
    y_action = HAUTEUR - charte.BARRE_ACTION
    ecran.ajouter(
        *barre_action_fixe(y_action, [bouton(M, y_action + 14, UTILE, "Envoyer la demande")])
    )

    return ecran
"""Ecran 5 — Detail d'un objet (fiche produit).

Objectif : consulter les informations detaillees d'un equipement partage puis
declencher une demande de pret.

Elements requis satisfaits : bouton retour, zone visuelle, titre,
disponibilite, batiment du campus, nom et note du proprietaire (4.8/5),
description textuelle, bouton d'action fixe en bas « Demander le pret ».
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    avatar,
    barre_action_fixe,
    barre_etat,
    bouton,
    etiquette_etat,
    hauteur_ligne,
    icone_agenda,
    icone_batiment,
    icone_coeur,
    icone_retour,
    notation,
    separateur_marge,
    vignette,
    visuel,
)
from ..donnees import trouver
from ..scene import H_CENTRE, H_DROITE, Ecran, Forme, Ligne, Texte

NOM = "05 · Détail de l'objet"

OBJET = trouver("Projecteur Epson EB-2150")

# Hauteur de la zone visuelle. Volontairement contenue : le contenu de la
# fiche doit tenir au-dessus de la barre d'action fixe sans defilement.
ZONE_VISUELLE = 216


def construire() -> Ecran:
    objet = OBJET
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 5 — Detail d'un objet. Retour, zone visuelle, titre, "
            "disponibilite, batiment, proprietaire + note, description, "
            "conditions, bouton fixe « Demander le pret »."
        ),
    )

    ecran.ajouter(*barre_etat(couleur="#FFFFFF"))

    # --- Zone visuelle : occupe toute la largeur, sous la barre de retour ---
    ecran.ajouter(*vignette(0, 0, LARGEUR, ZONE_VISUELLE, "#E4EBE4", visuel(objet.categorie)))

    # Barre superieure en surimpression : retour + actions.
    ecran.ajouter(*icone_retour(M + 11, 46, "#FFFFFF", 24))
    ecran.ajouter(*icone_coeur(LARGEUR - M - 22, 46, "#FFFFFF", 22))

    # Pastille de categorie, en bas de la zone visuelle.
    ecran.ajouter(
        Forme(M, ZONE_VISUELLE - 52, 118, 32, "#FFFFFF", 16, None, 0, nom="Badge / catégorie"),
        Texte(M, ZONE_VISUELLE - 45, 118, objet.categorie, 12, True, charte.VERT, H_CENTRE),
    )

    # --- Corps de la fiche, sur fond clair ---
    y = ZONE_VISUELLE + charte.ESP_5

    # Disponibilite + batiment.
    etat = etiquette_etat(objet)
    ecran.ajouter(
        Forme(M, y, etat.l, etat.h, etat.fond, etat.rayon, None, 0, nom="Badge / état"),
        Texte(M, y + 3, etat.l, objet.etat, etat.taille, True, etat.couleur_texte, H_CENTRE,
              hauteur=etat.h - 6),
    )
    y += etat.h + charte.ESP_3

    # Titre.
    ecran.ajouter(
        Texte(M, y, UTILE, objet.titre, charte.T_TITRE, True, charte.TEXTE,
              hauteur=hauteur_ligne(charte.T_TITRE, 1.2) * 2)
    )
    y += hauteur_ligne(charte.T_TITRE, 1.2) * 2 + charte.ESP_3

    # Localisation et duree de pret.
    ecran.ajouter(*icone_batiment(M + 8, y + 8, charte.TEXTE_SECONDAIRE))
    ecran.ajouter(
        Texte(M + 26, y, UTILE - 26, "%s · %s" % (objet.batiment, objet.duree),
              charte.T_LABEL, False, charte.TEXTE_SECONDAIRE)
    )
    y += hauteur_ligne(charte.T_LABEL) + charte.ESP_5

    # --- Carte proprietaire ---
    hauteur_proprio = 74
    ecran.ajouter(Forme(M, y, UTILE, hauteur_proprio, charte.SURFACE, charte.RAYON_CARTE,
                        charte.BORDURE, 1, nom="Carte / propriétaire"))
    ecran.ajouter(*avatar(M + 14, y + 15, 44, objet.proprietaire.initiales))
    ecran.ajouter(
        Texte(M + 68, y + 16, UTILE - 82, objet.proprietaire.nom, charte.T_CORPS_FORT, True,
              charte.TEXTE)
    )
    ecran.ajouter(
        Texte(M + 68, y + 34, UTILE - 82,
              "%s · %s" % (objet.proprietaire.filiere, objet.proprietaire.niveau),
              11, False, charte.TEXTE_DISCRET)
    )
    ecran.ajouter(*notation(objet.note, M + 68, y + 50, 12))
    ecran.ajouter(
        Texte(M + UTILE - 84, y + 52, 70, "%d échanges" % objet.proprietaire.nb_echanges,
              10, False, charte.TEXTE_DISCRET, H_DROITE)
    )
    y += hauteur_proprio + charte.ESP_5

    # --- Description ---
    ecran.ajouter(Texte(M, y, UTILE, "Description", charte.T_TITRE_SECTION, True, charte.TEXTE))
    y += hauteur_ligne(charte.T_TITRE_SECTION) + charte.ESP_2
    lignes_desc = 4
    hauteur_desc = lignes_desc * hauteur_ligne(charte.T_CORPS, 1.4)
    ecran.ajouter(
        Texte(M, y, UTILE, objet.description, charte.T_CORPS, False, charte.TEXTE_SECONDAIRE,
              hauteur=hauteur_desc)
    )
    y += hauteur_desc + charte.ESP_5

    # --- Conditions de pret ---
    ecran.ajouter(Texte(M, y, UTILE, "Conditions de prêt", charte.T_TITRE_SECTION, True, charte.TEXTE))
    y += hauteur_ligne(charte.T_TITRE_SECTION) + charte.ESP_3
    # Seules les deux premieres conditions sont visibles : le contenu long
    # defile, la maquette montre l'etat initial de l'ecran.
    for condition in objet.conditions[:2]:
        ecran.ajouter(Forme(M + 2, y + 6, 5, 5, charte.VERT, 2.5))
        ecran.ajouter(
            Texte(M + 16, y, UTILE - 16, condition, charte.T_LABEL, False, charte.TEXTE_SECONDAIRE,
                  hauteur=hauteur_ligne(charte.T_LABEL, 1.4))
        )
        y += hauteur_ligne(charte.T_LABEL, 1.4) + charte.ESP_2

    # --- Action fixe en bas ---
    y_action = HAUTEUR - charte.BARRE_ACTION
    ecran.ajouter(*barre_action_fixe(y_action, [bouton(M, y_action + 14, UTILE, "Demander le prêt")]))

    return ecran
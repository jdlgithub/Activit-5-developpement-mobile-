"""Ecran 8 — Profil et gestion des annonces.

Objectif : gerer son profil, ses annonces publiees et ses emprunts.

Elements requis satisfaits : en-tete (avatar, nom, filiere, score de
confiance), onglets « Mes annonces » / « Mes emprunts », liste des objets avec
actions rapides (Modifier / Supprimer), bouton de deconnexion.
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    avatar,
    barre_etat,
    barre_onglets,
    bouton,
    carte_objet_ligne,
    entete_onglets,
    hauteur_ligne,
    notation,
)
from ..donnees import MOI, OBJETS
from ..scene import H_CENTRE, H_DROITE, Ecran, Forme, Ligne, Texte

NOM = "08 · Profil & annonces"

# Objets « en cours » sur le profil : l'onglet « Mes annonces » est actif.
MES_ANNONCES = OBJETS[:2]
MES_EMPRUNTS = OBJETS[2:4]

HAUTEUR_LIGNE = 96


def construire() -> Ecran:
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 8 — Profil et gestion des annonces. Avatar, nom, filiere, "
            "score de confiance, onglets « Mes annonces » / « Mes emprunts », "
            "liste avec actions Modifier / Supprimer, deconnexion."
        ),
    )

    ecran.ajouter(*barre_etat())

    # --- Titre ---
    y = 40
    ecran.ajouter(
        Texte(0, y, LARGEUR, "Mon profil", charte.T_TITRE, True, charte.TEXTE, align_h=1)
    )
    y += hauteur_ligne(charte.T_TITRE) + charte.ESP_4

    # --- En-tete : avatar + identite + score de confiance ---
    hauteur_entete = 96
    ecran.ajouter(Forme(M, y, UTILE, hauteur_entete, charte.SURFACE, charte.RAYON_CARTE,
                        charte.BORDURE, 1, nom="Carte / identité"))
    ecran.ajouter(*avatar(M + 16, y + 18, 60, MOI.initiales, charte.VERT_CLAIR, charte.VERT, 22))

    ecran.ajouter(
        Texte(M + 88, y + 20, UTILE - 100, MOI.nom, charte.T_TITRE_SECTION, True, charte.TEXTE)
    )
    ecran.ajouter(
        Texte(M + 88, y + 44, UTILE - 100, "%s · %s" % (MOI.filiere, MOI.niveau), 11, False,
              charte.TEXTE_DISCRET)
    )

    # Score de confiance : note + nombre d'echanges, mis en avant en orange doux.
    ecran.ajouter(
        Forme(M + 88, y + 62, 150, 24, charte.ORANGE_CLAIR, 12, None, 0, nom="Score / confiance"),
        *notation(MOI.note, M + 98, y + 64, 11, charte.ORANGE_FONCE),
    )
    ecran.ajouter(
        Texte(M + UTILE - 96, y + 66, 80, "%d échanges" % MOI.nb_echanges, 10, False,
              charte.TEXTE_SECONDAIRE, H_DROITE)
    )
    y += hauteur_entete + charte.ESP_4

    # --- Indicateurs cles ---
    ecran.ajouter(*_ligne_stats(M, y, UTILE))
    y += 64 + charte.ESP_4

    # --- Onglets ---
    ecran.ajouter(*entete_onglets(M, y, ("Mes annonces", "Mes emprunts"), actif=0, l=UTILE))
    y += 40 + charte.ESP_3

    # --- Liste des annonces avec actions rapides ---
    for objet in MES_ANNONCES:
        ecran.ajouter(*carte_objet_ligne(M, y, UTILE, objet, HAUTEUR_LIGNE, actions=True))
        y += HAUTEUR_LIGNE + charte.ESP_3

    # --- Deconnexion ---
    ecran.ajouter(bouton(M, y + charte.ESP_2, UTILE, "Se déconnecter", variante="danger",
                         taille=charte.T_CORPS_FORT))

    # --- Navigation inferieure ---
    ecran.ajouter(*barre_onglets(actif="profil"))

    return ecran


def _ligne_stats(x, y, l) -> list:
    """Trois indicateurs cles : annonces, emprunts, score eco."""
    elements = [
        ("12", "annonces"),
        ("5", "emprunts"),
        ("4,9", "score"),
    ]
    largeur_case = l / len(elements)
    morceaux = [Forme(x, y, l, 64, charte.SURFACE, charte.RAYON_CARTE, charte.BORDURE, 1,
                       nom="Stats / fond")]
    for i, (valeur, libelle) in enumerate(elements):
        cx = x + largeur_case * (i + 0.5)
        morceaux.append(
            Texte(x + largeur_case * i, y + 13, largeur_case, valeur, 18, True, charte.VERT,
                  H_CENTRE)
        )
        morceaux.append(
            Texte(x + largeur_case * i, y + 38, largeur_case, libelle, 10, False,
                  charte.TEXTE_DISCRET, H_CENTRE)
        )
        if i:
            morceaux.append(Ligne(x + largeur_case * i, y + 16, x + largeur_case * i, y + 48,
                                  charte.BORDURE, 1))
    return morceaux
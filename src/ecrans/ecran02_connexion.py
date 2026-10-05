"""Ecran 2 — Connexion.

Objectif : authentifier un etudiant existant. Un seul ecran, une seule action
principale, le minimum de champs (email institutionnel + mot de passe).

Elements requis satisfaits : titre « Bon retour ! », champ email
institutionnel, champ mot de passe masque, lien « Mot de passe oublie ? »,
bouton « Se connecter », lien vers l'inscription.
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    barre_etat,
    bouton,
    champ,
    hauteur_champ,
    hauteur_ligne,
    icone_oeil,
    icone_retour,
    logo,
)
from ..scene import H_CENTRE, H_DROITE, Ecran, Forme, Texte

NOM = "02 · Connexion"


def construire() -> Ecran:
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 2 — Connexion. Titre, email institutionnel, mot de passe "
            "masque, lien mot de passe oublie, bouton Se connecter, lien "
            "vers l'inscription."
        ),
    )

    ecran.ajouter(*barre_etat())

    # --- Barre superieure : retour + marque discrete ---
    y = 34
    ecran.ajouter(*icone_retour(M + 11, y + 22, charte.TEXTE))
    ecran.ajouter(*logo(LARGEUR - M - 18, y + 22, 28))

    # --- Titre et sous-titre ---
    y += 68
    ecran.ajouter(Texte(M, y, UTILE, "Bon retour !", charte.T_TITRE, True, charte.TEXTE))
    y += hauteur_ligne(charte.T_TITRE) + 6
    ecran.ajouter(
        Texte(
            M, y, UTILE,
            "Connectez-vous avec votre adresse<br>institutionnelle pour emprunter.",
            charte.T_CORPS, False, charte.TEXTE_SECONDAIRE,
            hauteur=hauteur_ligne(charte.T_CORPS, 1.35) * 2,
        )
    )
    y += hauteur_ligne(charte.T_CORPS, 1.35) * 2 + charte.ESP_6

    # --- Formulaire, dans une carte pour regrouper la zone d'action ---
    hauteur_form = (
        hauteur_champ(True, aide=True)      # email
        + charte.ESP_4
        + hauteur_champ(True)               # mot de passe
        + charte.ESP_2
        + hauteur_ligne(charte.T_LABEL)     # lien mot de passe oublie
        + 2 * charte.ESP_4
    )
    ecran.ajouter(Forme(M, y, UTILE, hauteur_form, charte.SURFACE, charte.RAYON_CARTE, charte.BORDURE, 1,
                        nom="Carte / formulaire"))

    y += charte.ESP_4
    ecran.ajouter(*champ(M + charte.ESP_4, y, UTILE - 2 * charte.ESP_4, "Email institutionnel",
                         "prenom.nom@univ-campus.fr",
                         aide="Uniquement votre adresse @univ-campus.fr"))
    y += hauteur_champ(True, aide=True) + charte.ESP_4

    # Champ mot de passe : valeur masquee + icone oeil (afficher/masquer).
    ecran.ajouter(*champ(M + charte.ESP_4, y, UTILE - 2 * charte.ESP_4, "Mot de passe",
                         "•" * 8, icone=None))
    y_mdp = y + hauteur_ligne(charte.T_LABEL) + charte.ESP_1
    ecran.ajouter(*icone_oeil(M + UTILE - charte.ESP_4 - 14, y_mdp + charte.CHAMP_H / 2, charte.TEXTE_DISCRET, 18))
    y += hauteur_champ(True) + charte.ESP_2

    # Lien « Mot de passe oublie ? » aligne a droite, cible tactile 44 px.
    hauteur_lien = charte.CIBLE_MIN
    ecran.ajouter(
        Texte(M + charte.ESP_4, y + (hauteur_lien - hauteur_ligne(charte.T_LABEL)) / 2,
              UTILE - 2 * charte.ESP_4, "Mot de passe oublié ?", charte.T_LABEL, True,
              charte.VERT, H_DROITE, hauteur=hauteur_lien)
    )

    # --- Action principale ---
    y += hauteur_lien + charte.ESP_4
    ecran.ajouter(bouton(M, y, UTILE, "Se connecter"))
    y += charte.BOUTON_H

    # --- Acces a l'inscription ---
    y += charte.ESP_6
    ecran.ajouter(
        Texte(
            0, y, LARGEUR,
            "Pas encore de compte ? <b>S'inscrire</b>", charte.T_CORPS, False,
            charte.TEXTE_SECONDAIRE, H_CENTRE,
        )
    )

    # --- Pied de page : rappel du caractere reserve aux etudiants ---
    ecran.ajouter(
        Texte(
            0, HAUTEUR - 58, LARGEUR,
            "CampusShare — le partage de matériel entre étudiants",
            11, False, charte.TEXTE_DISCRET, H_CENTRE,
        )
    )

    return ecran
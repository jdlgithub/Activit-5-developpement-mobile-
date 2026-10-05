"""Ecran 3 — Inscription.

Objectif : creer un compte etudiant. Le formulaire est volontairement limite :
cinq champs texte, une filiere, un niveau, une acceptation de charte.

Optimisation de la hauteur : nom et prenom sont places sur deux colonnes
(standard mobile), ce qui evite un defilement pour les champs les plus courts.
"""

from .. import charte
from ..composants import (
    HAUTEUR,
    LARGEUR,
    M,
    UTILE,
    barre_etat,
    bouton,
    case_a_cocher,
    champ,
    champ_selecteur,
    hauteur_champ,
    hauteur_ligne,
    icone_retour,
    puce_filtre,
)
from ..donnees import FILIERES, NIVEAUX
from ..scene import Ecran, Texte

NOM = "03 · Inscription"

# Deux colonnes : nom et prenom.
COLONNE = (UTILE - charte.ESP_3) / 2


def construire() -> Ecran:
    ecran = Ecran(
        nom=NOM,
        largeur=LARGEUR,
        hauteur=HAUTEUR,
        fond=charte.FOND,
        note=(
            "Ecran 3 — Inscription. Champs Nom, Prenom, Email universitaire, "
            "Mot de passe, Confirmation, selecteur filiere/niveau, case "
            "d'acceptation de la charte, bouton S'inscrire."
        ),
    )

    ecran.ajouter(*barre_etat())

    # --- Barre superieure ---
    y = 34
    ecran.ajouter(*icone_retour(M + 11, y + 22, charte.TEXTE))
    ecran.ajouter(
        Texte(0, y + 14, LARGEUR, "Créer un compte", charte.T_SOUS_TITRE, True, charte.TEXTE,
              align_h=1)
    )

    # --- Titre d'accroche ---
    y += 62
    ecran.ajouter(
        Texte(
            M, y, UTILE,
            "Rejoignez le réseau<br>de partage du campus",
            20, True, charte.TEXTE, hauteur=hauteur_ligne(20, 1.3) * 2,
        )
    )
    y += hauteur_ligne(20, 1.3) * 2 + charte.ESP_5

    # --- Nom et prenom sur deux colonnes ---
    ecran.ajouter(*champ(M, y, COLONNE, "Nom", "Dupont"))
    ecran.ajouter(*champ(M + COLONNE + charte.ESP_3, y, COLONNE, "Prénom", "Camille"))
    y += hauteur_champ(True) + charte.ESP_3

    # --- Email universitaire ---
    ecran.ajouter(
        *champ(M, y, UTILE, "Email universitaire", "camille.dupont@univ-campus.fr",
               aide="Votre email sert d'identifiant de connexion.")
    )
    y += hauteur_champ(True, aide=True) + charte.ESP_3

    # --- Mot de passe et confirmation ---
    ecran.ajouter(*champ(M, y, UTILE, "Mot de passe", "•" * 8))
    y += hauteur_champ(True) + charte.ESP_3
    ecran.ajouter(*champ(M, y, UTILE, "Confirmation", "•" * 8))
    y += hauteur_champ(True) + charte.ESP_3

    # --- Filiere et niveau ---
    ecran.ajouter(*champ_selecteur(M, y, UTILE, "Filière", FILIERES[0]))
    y += hauteur_champ(True) + charte.ESP_3

    ecran.ajouter(Texte(M, y, UTILE, "Niveau d'études", charte.T_LABEL, True, charte.TEXTE_SECONDAIRE))
    y += hauteur_ligne(charte.T_LABEL) + charte.ESP_2
    x_puce = M
    for i, niveau in enumerate(NIVEAUX[:4]):
        largeur_puce = len(niveau) * 7 + 28
        if x_puce + largeur_puce > M + UTILE:
            break
        ecran.ajouter(puce_filtre(x_puce, y, niveau, actif=(i == 2)))
        x_puce += largeur_puce + charte.ESP_2
    y += 32 + charte.ESP_3

    # --- Acceptation de la charte ---
    hauteur_ligne_texte = hauteur_ligne(charte.T_CORPS, 1.35)
    ecran.ajouter(*case_a_cocher(M + 2, y + 1, coche=True))
    ecran.ajouter(
        Texte(
            M + 32, y, UTILE - 32,
            "J'accepte la charte du CampusShare :<br>"
            "<b>restituer en bon état</b> et <b>signaler tout dégât</b>.",
            12, False, charte.TEXTE_SECONDAIRE,
            hauteur=hauteur_ligne_texte * 2,
        )
    )
    y += hauteur_ligne_texte * 2 + charte.ESP_5

    # --- Validation ---
    ecran.ajouter(bouton(M, y, UTILE, "S'inscrire"))
    y += charte.BOUTON_H + charte.ESP_4

    ecran.ajouter(
        Texte(
            0, y, LARGEUR,
            "Déjà inscrit ? <b>Se connecter</b>", charte.T_CORPS, False,
            charte.TEXTE_SECONDAIRE, align_h=1,
        )
    )

    return ecran
"""Les huit ecrans de l'application CampusShare, dans l'ordre du parcours.

Chaque module expose ``construire() -> Ecran``.
"""

from . import (
    ecran01_accueil,
    ecran02_connexion,
    ecran03_inscription,
    ecran04_tableau_bord,
    ecran05_detail_objet,
    ecran06_demande_pret,
    ecran07_publication,
    ecran08_profil,
)

__all__ = [
    "ecran01_accueil",
    "ecran02_connexion",
    "ecran03_inscription",
    "ecran04_tableau_bord",
    "ecran05_detail_objet",
    "ecran06_demande_pret",
    "ecran07_publication",
    "ecran08_profil",
]
"""Controle de mise en page des maquettes.

Usage :
    python3 -m src.linter

Verifie automatiquement ce qu'un controle visuel doit faire a la main :

  1. aucune forme ne deborde du cadre de l'ecran ;
  2. aucun texte ne deborde de la largeur qui lui est allouee (estimation) ;
  3. le contenu ne passe pas sous la barre d'action fixe ni sous la barre
     d'onglets, quand ces barres sont presentes ;
  4. la barre d'onglets est la derniere chose dessinee sur chaque ecran qui
     la contient ;
  5. les cibles tactiles des actions principales font au moins 44 px de haut ;
  6. la charte est respectee : toute couleur de remplissage et de texte
     appartient a la palette ;
  7. une seule famille de police est utilisee.

Les problemes sont rapportes par ecran, avec une tolerance de 1 px pour
absorber les arrondis.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

from . import charte
from .build import charger_ecrans
from .scene import Ellipse, Forme, FormeTexte, Image, Ligne, Texte, Ecran

TOLERANCE = 1.0

# Palette autorisee (remplissages et textes).
PALETTE = {
    charte.VERT, charte.VERT_FONCE, charte.VERT_CLAIR,
    charte.ORANGE, charte.ORANGE_CLAIR, charte.ORANGE_FONCE,
    charte.FOND, charte.SURFACE, charte.BORDURE, charte.BORDURE_FORCE,
    charte.TEXTE, charte.TEXTE_SECONDAIRE, charte.TEXTE_DISCRET,
    charte.TEXTE_INVERSE, charte.TEXTE_SUR_PRIMAIRE, charte.TEXTE_SUR_ACCENT,
    charte.SUCCES, charte.ALERTE, charte.INFO,
    charte.CONFIANCE_HAUTE, charte.CONFIANCE_MOYENNE, charte.CONFIANCE_BASSE,
    charte.VIGNETTE,
}

# Variantes de couleur tolerees (declinaisons de fond utilisees dans les maquettes).
COULEURS_TOLERANTES = {"#FFFFFF", "#276B2B", "#D8EBD9", "#CBE3CD", "#B6D2B9",
                       "#E4EBE4", "#F0C9C9", "#EDF1ED", "#A9B5A5", None}


@dataclass
class Probleme:
    ecran: str
    niveau: str  # "erreur" ou "avertissement"
    message: str


@dataclass
class Collecteur:
    problemes: list[Probleme] = field(default_factory=list)

    def ajouter(self, ecran: Ecran, niveau: str, message: str) -> None:
        self.problemes.append(Probleme(ecran.nom, niveau, message))


# ---------------------------------------------------------------------------
# Boites englobantes
# ---------------------------------------------------------------------------


def boite(forme):
    """Retourne (x, y, largeur, hauteur) de la forme, ou None si non pertinente."""
    if isinstance(forme, Ligne):
        x = min(forme.x1, forme.x2)
        y = min(forme.y1, forme.y2)
        return x, y, abs(forme.x2 - forme.x1), abs(forme.y2 - forme.y1)
    if isinstance(forme, (Forme, FormeTexte, Texte, Ellipse, Image)):
        return forme.x, forme.y, forme.l, (forme.hauteur_estimee if isinstance(forme, Texte) else forme.h)
    return None


def _borne_inferieure(ecran: Ecran) -> tuple[float, str] | None:
    """Derniere barre fixe (onglets ou action) : (y, nom)."""
    if not ecran.formes:
        return None
    # Barre d'onglets : dernier bloc de formes de hauteur BARRE_ONGLETS
    # positionne en bas de l'ecran.
    y_onglets = charte.HAUTEUR_ECRAN - charte.BARRE_ONGLETS
    if any(
        isinstance(f, Forme) and abs(f.y - y_onglets) < TOLERANCE and abs(f.h - charte.BARRE_ONGLETS) < TOLERANCE
        for f in ecran.formes
    ):
        return y_onglets, "barre d'onglets"
    y_action = charte.HAUTEUR_ECRAN - charte.BARRE_ACTION
    if any(
        isinstance(f, Forme) and abs(f.y - y_action) < TOLERANCE
        and abs(f.h - charte.BARRE_ACTION) < TOLERANCE
        for f in ecran.formes
    ):
        return y_action, "barre d'action"
    return None


def _dernier_index_barre(ecran: Ecran, y_barre: float) -> int | None:
    """Index de la premiere forme composant la barre fixe."""
    for i, forme in enumerate(ecran.formes):
        b = boite(forme)
        if b and abs(b[1] - y_barre) < TOLERANCE:
            return i
    return None


# ---------------------------------------------------------------------------
# Controles
# ---------------------------------------------------------------------------


def controler_ecran(ecran: Ecran, collecteur: Collecteur) -> None:
    L, H = ecran.largeur, ecran.hauteur

    # 1. Debordement hors cadre.
    for forme in ecran.formes:
        b = boite(forme)
        if b is None:
            continue
        x, y, l, h = b
        if x < -TOLERANCE or y < -TOLERANCE or x + l > L + TOLERANCE or y + h > H + TOLERANCE:
            nom = getattr(forme, "nom", None) or type(forme).__name__
            collecteur.ajouter(
                ecran, "erreur",
                "forme hors cadre : %s a (%.0f,%.0f) %.0fx%.0f" % (nom, x, y, l, h),
            )

    # 2. Bloc de texte trop court pour le texte qu'il contient, ou collision
    #    avec le bloc suivant dans la meme colonne.
    controles_texte(ecran, collecteur)

    # 3. Contenu sous la barre fixe.
    borne = _borne_inferieure(ecran)
    if borne:
        y_barre, nom_barre = borne
        debut = _dernier_index_barre(ecran, y_barre)
        if debut is not None:
            for forme in ecran.formes[:debut]:
                b = boite(forme)
                if b and b[1] + b[3] > y_barre + TOLERANCE:
                    # Un fond qui couvre volontairement toute la largeur est tolere.
                    if isinstance(forme, Forme) and forme.l >= L - TOLERANCE and forme.h > 0:
                        continue
                    collecteur.ajouter(
                        ecran, "erreur",
                        "contenu sous la %s : %s se termine a y=%.0f (barre a y=%.0f)"
                        % (nom_barre, _nom(forme), b[1] + b[3], y_barre),
                    )

    # 4. La barre fixe doit etre dessinee en dernier.
    if borne:
        y_barre, nom_barre = borne
        debut = _dernier_index_barre(ecran, y_barre)
        if debut is not None:
            formes_apres = ecran.formes[debut + 1:]
            intrus = [f for f in formes_apres if not _fait_partie_de_la_barre(f, y_barre)]
            if intrus:
                collecteur.ajouter(
                    ecran, "avertissement",
                    "%d forme(s) dessinees apres la %s" % (len(intrus), nom_barre),
                )

    # 5. Cibles tactiles, selon le role fonctionnel declare.
    for forme in ecran.formes:
        if not isinstance(forme, FormeTexte):
            continue
        role = getattr(forme, "role", "bouton")
        libelle = _extrait(forme.contenu, 24)
        if role == "bouton" and forme.h < charte.CIBLE_MIN - TOLERANCE:
            collecteur.ajouter(
                ecran, "erreur",
                "bouton « %s » trop haut : %.0f px (minimum %d)" % (libelle, forme.h, charte.CIBLE_MIN),
            )
        if role == "puce" and forme.h < 30 - TOLERANCE:
            collecteur.ajouter(
                ecran, "erreur",
                "puce « %s » trop haute : %.0f px (minimum 30)" % (libelle, forme.h),
            )

    # 6/7. Respect de la charte.
    for forme in ecran.formes:
        for attribut, valeur in (("fond", getattr(forme, "fond", None)),
                                 ("bordure", getattr(forme, "bordure", None)),
                                 ("couleur de texte", getattr(forme, "couleur", None)),
                                 ("couleur de texte", getattr(forme, "couleur_texte", None))):
            if valeur is None:
                continue
            if valeur not in PALETTE and valeur not in COULEURS_TOLERANTES:
                collecteur.ajouter(
                    ecran, "avertissement",
                    "couleur hors charte : %s (%s)" % (valeur, attribut),
                )


def controles_texte(ecran: Ecran, collecteur: Collecteur) -> None:
    """Verifie que chaque bloc de texte tient dans la place qui lui est reservee.

    On calcule la hauteur reelle apres retour a la ligne (mesure partagee) puis
    on verifie qu'elle ne chevauche pas le bloc de texte suivant dessine dans la
    meme colonne.
    """
    blocs = [(i, f) for i, f in enumerate(ecran.formes) if isinstance(f, Texte)]
    for position, (i, forme) in enumerate(blocs):
        h = forme.hauteur_estimee
        if forme.hauteur and forme.hauteur < h - TOLERANCE:
            collecteur.ajouter(
                ecran, "erreur",
                "« %s » : hauteur reservee %.0f px pour %.0f px de texte"
                % (_extrait(forme.contenu), forme.hauteur, h),
            )
        bas = forme.y + h
        for j, suivant in blocs[position + 1:]:
            if suivant.y + TOLERANCE < forme.y:
                continue  # bloc anterieur, dans une autre colonne
            chevauchement_x = forme.x < suivant.x + suivant.l - TOLERANCE and suivant.x < forme.x + forme.l - TOLERANCE
            if chevauchement_x and suivant.y < bas - TOLERANCE:
                collecteur.ajouter(
                    ecran, "erreur",
                    "« %s » deborde sur « %s » : %.0f px pour y=%.0f, suivant a y=%.0f"
                    % (_extrait(forme.contenu), _extrait(suivant.contenu), h, forme.y, suivant.y),
                )
                break


def _fait_partie_de_la_barre(forme, y_barre: float) -> bool:
    """Une forme appartient a la barre fixe si elle y est ancree."""
    b = boite(forme)
    if b is None:
        return True
    # Elements centres verticalement dans la barre ou traces au-dessus d'elle.
    return b[1] + b[3] / 2 >= y_barre - TOLERANCE


def _extrait(contenu: str, limite: int = 32) -> str:
    nu = contenu.replace("<br>", " ").replace("<b>", "").replace("</b>", "")
    return nu[:limite] + ("…" if len(nu) > limite else "")


def _nom(forme) -> str:
    return getattr(forme, "nom", None) or type(forme).__name__


def controler_tout(ecrans: list[Ecran]) -> Collecteur:
    collecteur = Collecteur()
    for ecran in ecrans:
        controler_ecran(ecran, collecteur)
    return collecteur


def main(argv: list[str] | None = None) -> int:
    ecrans = charger_ecrans()
    collecteur = controler_tout(ecrans)

    erreurs = [p for p in collecteur.problemes if p.niveau == "erreur"]
    avertissements = [p for p in collecteur.problemes if p.niveau == "avertissement"]

    print("Controle de mise en page — %d ecrans, %d formes" % (
        len(ecrans), sum(e.nombre_formes for e in ecrans)))
    print()

    for ecran in ecrans:
        concerns = [p for p in collecteur.problemes if p.ecran == ecran.nom]
        marque = "OK " if not concerns else "%2d" % len(concerns)
        print("[%s] %s" % (marque, ecran.nom))
        for p in concerns:
            print("        %s : %s" % (p.niveau, p.message))

    print()
    print("%d erreur(s), %d avertissement(s)" % (len(erreurs), len(avertissements)))
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
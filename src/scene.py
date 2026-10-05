"""Scene graphique : representation intermediaire des maquettes.

Les ecrans sont decrits une seule fois sous forme de primitives
positionnees en pixels. Deux moteurs de rendu consomment cette scene :

  1. PencilDocumentWriter  -> fichier .epgz ouvrable dans Pencil ;
  2. SVGSceneRenderer      -> apercus SVG/PNG pour verification visuelle.

Ce decoupage garantit que l'apercu et le document Pencil restent identiques.

Modele de donnees (reverse-engineere depuis les sources evolus/pencil v3) :
  - une forme est un noeud <svg:g p:type="Shape" p:def="..."> ;
  - la position est portee par l'attribut SVG transform="translate(x,y)" ;
  - la taille est portee par la propriete "box" au format "largeur,hauteur" ;
  - les autres proprietes sont des <p:property name="..."> en CDATA.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Alignement (semantique identique a celle de Pencil : h,v)
# ---------------------------------------------------------------------------

H_GAUCHE, H_CENTRE, H_DROITE = 0, 1, 2
V_HAUT, V_CENTRE, V_BAS = 0, 1, 2


@dataclass
class Forme:
    """Forme de base : un rectangle plein avec bord arrondi."""

    x: float
    y: float
    l: float
    h: float
    fond: str | None = None
    rayon: float = 0.0
    bordure: str | None = None
    epaisseur: float = 0.0
    # Style de bordure (dash, etc.). "solid" par defaut.
    style_bordure: str = "solid"
    # Metadata Pencil facultative : libelle de calque, etc.
    nom: str | None = None

    def properties(self) -> dict[str, Any]:
        return {
            "box": "%g,%g" % (self.l, self.h),
            "fillColor": self.fond,
            "strokeColor": self.bordure,
            "strokeStyle": "%g|%s" % (round(self.epaisseur), self.style_bordure),
            "radius": "%g,%g" % (self.rayon, self.rayon),
            "withBlur": "false",
            "textContent": "",
            "textFont": "",
            "textColor": "",
            "textAlign": "0,0",
            "textPadding": "0,10",
        }


@dataclass
class Texte:
    """Bloc de texte (HTML). La hauteur est calculee a la maquette."""

    x: float
    y: float
    l: float
    contenu: str
    taille: int = 14
    gras: bool = False
    couleur: str = "#000000"
    align_h: int = H_GAUCHE
    align_v: int = V_HAUT
    hauteur: float = 0.0  # si 0, calculee a partir de la taille de police
    interligne: float = 1.25
    style: str = ""  # CSS additionnel
    # Metadata Pencil facultative.
    nom: str | None = None

    def properties(self) -> dict[str, Any]:
        return {
            "fixedWidth": "true",
            "width": "%g,0" % self.l,
            "textContent": self.contenu,
            "textFont": police(self.taille, self.gras),
            "textColor": self.couleur,
            "customStyle": self.style,
        }

    @property
    def hauteur_estimee(self) -> float:
        """Hauteur du bloc, retour a la ligne compris (mesure partagee)."""
        from .mesure import hauteur_texte

        return hauteur_texte(
            self.contenu, self.l, self.taille, self.gras, self.interligne
        )


@dataclass
class FormeTexte:
    """Rectangle portant du texte centre (utilise pour les boutons).

    Regroupe une forme et un texte afin de garantir leur synchronisation.
    """

    x: float
    y: float
    l: float
    h: float
    contenu: str
    taille: int = 15
    gras: bool = True
    fond: str = "#2E7D32"
    couleur_texte: str = "#FFFFFF"
    align_h: int = H_CENTRE
    align_v: int = V_CENTRE
    rayon: float = 10
    bordure: str | None = None
    epaisseur: float = 0.0
    padding_v: float = 0.0
    # Role fonctionnel : pilote la regle de taille de cible tactile.
    #   "bouton" -> action, doit faire au moins CIBLE_MIN de haut
    #   "badge"  -> pastille d'etat informative (22-24 px)
    #   "puce"   -> puce de filtre, cible tactile de 32 px + zone elargie
    #   "lien"   -> lien textuel, pas de zone tactile imposee
    role: str = "bouton"
    # Metadata Pencil facultative : libelle de calque.
    nom: str | None = None

    def properties(self) -> dict[str, Any]:
        return {
            "box": "%g,%g" % (self.l, self.h),
            "fillColor": self.fond,
            "strokeColor": self.bordure,
            "strokeStyle": "%g|solid" % round(self.epaisseur),
            "radius": "%g,%g" % (self.rayon, self.rayon),
            "withBlur": "false",
            "textContent": self.contenu,
            "textFont": police(self.taille, self.gras),
            "textColor": self.couleur_texte,
            "textAlign": "%d,%d" % (self.align_h, self.align_v),
            "textPadding": "0,%g" % self.padding_v,
        }


@dataclass
class Ligne:
    """Segment droit."""

    x1: float
    y1: float
    x2: float
    y2: float
    couleur: str = "#000000"
    epaisseur: float = 1.0
    nom: str | None = None


@dataclass
class Ellipse:
    """Ellipse (utilisee pour les pastilles d'avatar et les pastilles d'etat)."""

    x: float
    y: float
    l: float
    h: float
    fond: str | None = None
    bordure: str | None = None
    epaisseur: float = 0.0
    nom: str | None = None

    def properties(self) -> dict[str, Any]:
        return {
            "box": "%g,%g" % (self.l, self.h),
            "fillColor": self.fond,
            "strokeColor": self.bordure,
            "strokeStyle": "%g|solid" % round(self.epaisseur),
        }


@dataclass
class Image:
    """Image matricielle (base64). Rendue par la forme Bitmap de Pencil."""

    x: float
    y: float
    l: float
    h: float
    donnees: str  # data URI complete
    nom: str | None = None

    def properties(self) -> dict[str, Any]:
        return {
            "box": "%g,%g" % (self.l, self.h),
            "imageData": self.donnees,
            "stretch": "true",
        }


# ---------------------------------------------------------------------------
# Fabrique de polices au format Pencil : "famille|poids|style|taille|decor"
# ---------------------------------------------------------------------------

_TAILLE_PX = "{size}px"


def police(taille: int, gras: bool = False, fromage: str = "none") -> str:
    """Construit la propriete de police Pencil."""
    from . import charte  # import tardif pour eviter un cycle

    return "%s|%s|normal|%s|%s" % (
        charte.POLICE,
        "bold" if gras else "normal",
        _TAILLE_PX.format(size=taille),
        fromage,
    )


def texte_brut(valeur: str) -> str:
    """Echappe une chaine destined a etre injectee dans du HTML."""
    return html.escape(valeur, quote=False)


# ---------------------------------------------------------------------------
# Scene et Ecran
# ---------------------------------------------------------------------------


@dataclass
class Ecran:
    """Une page de maquette (une page Pencil)."""

    nom: str
    largeur: int
    hauteur: int
    fond: str
    formes: list[Any] = field(default_factory=list)
    # Description de l'ecran, incluse dans les proprietes de page Pencil.
    note: str = ""
    # Ecran "de reference" heritee par d'autres pages (non utilise ici).
    parent: str | None = None

    def ajouter(self, *formes: Any) -> "Ecran":
        self.formes.extend(formes)
        return self

    @property
    def nombre_formes(self) -> int:
        return len(self.formes)
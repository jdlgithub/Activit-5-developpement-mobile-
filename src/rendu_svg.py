"""Rendu SVG d'une scene, pour les apercus de verification.

Reproduit le rendu que Pencil obtient en evaluant les comportements de ses
formes natives :
  - Forme      -> <rect>
  - FormeTexte -> <rect> + texte centre dans une foreignObject
  - Texte      -> <foreignObject> (comme la forme RichTextBoxV2)
  - Ligne      -> <line>
  - Ellipse    -> <ellipse>
  - Image      -> <image>

La police est stockee au format Pencil "famille|poids|style|taille|decor" ;
elle est convertie ici en CSS.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from . import charte
from .scene import Ecran, Ellipse, Forme, FormeTexte, Image, Ligne, Texte

NS_SVG = "http://www.w3.org/2000/svg"
NS_XHTML = "http://www.w3.org/1999/xhtml"

_ALIGN_H_CSS = {0: "left", 1: "center", 2: "right"}
_ALIGN_V_CSS = {0: "flex-start", 1: "center", 2: "flex-end"}


def _css_texte(forme: Texte) -> str:
    """Feuille de style du div, equivalente a customStyle + police + couleur."""
    base = (
        "margin:0; padding:0; font-family:%s; font-size:%s; font-weight:%s; color:%s;"
        " line-height:%s; %s"
        % (
            charte.POLICE,
            "%dpx" % forme.taille,
            "bold" if forme.gras else "normal",
            forme.couleur,
            forme.interligne,
            forme.style,
        )
    )
    return base


def _rect(forme: Forme) -> str:
    rx = min(forme.rayon, forme.l / 2, forme.h / 2) if forme.rayon else 0
    style = []
    style.append("fill:%s" % (forme.fond if forme.fond else "none"))
    if forme.bordure and forme.epaisseur:
        style.append("stroke:%s" % forme.bordure)
        style.append("stroke-width:%g" % forme.epaisseur)
        if forme.style_bordure and forme.style_bordure != "solid":
            style.append("stroke-dasharray:%s" % _dash(forme.style_bordure))
    attributs = 'x="%g" y="%g" width="%g" height="%g"' % (forme.x, forme.y, forme.l, forme.h)
    if rx:
        attributs += ' rx="%g" ry="%g"' % (rx, rx)
    return '<rect %s style="%s"/>' % (attributs, ";".join(style))


def _dash(style: str) -> str:
    return {
        "dashed": "6 4",
        "dotted": "2 3",
        "dot": "2 3",
        "dash": "6 4",
    }.get(style, "none")


def _forme_texte(forme: FormeTexte) -> str:
    base = Forme(
        forme.x, forme.y, forme.l, forme.h, forme.fond, forme.rayon,
        forme.bordure, forme.epaisseur,
    )
    pieces = [_rect(base)]
    style_div = (
        "display:flex; align-items:%s; justify-content:%s; height:100%%; width:100%%;"
        " font-family:%s; font-size:%dpx; font-weight:%s; color:%s;"
        " line-height:1.2; text-align:%s; box-sizing:border-box; padding:%gpx;"
        % (
            _ALIGN_V_CSS.get(forme.align_v, "center"),
            _ALIGN_H_CSS.get(forme.align_h, "center"),
            charte.POLICE, forme.taille,
            "bold" if forme.gras else "normal",
            forme.couleur_texte,
            _ALIGN_H_CSS.get(forme.align_h, "center"),
            forme.padding_v,
        )
    )
    pieces.append(
        '<foreignObject x="%g" y="%g" width="%g" height="%g"><div xmlns="%s" style="%s">%s</div></foreignObject>'
        % (forme.x, forme.y, forme.l, forme.h, NS_XHTML, style_div, forme.contenu)
    )
    return "".join(pieces)


def _texte(forme: Texte) -> str:
    hauteur = forme.hauteur_estimee
    style = _css_texte(forme) + "width:%gpx;" % forme.l
    return (
        '<foreignObject x="%g" y="%g" width="%g" height="%g"><div xmlns="%s" style="%s">%s</div></foreignObject>'
        % (forme.x, forme.y, forme.l, hauteur, NS_XHTML, style, forme.contenu)
    )


def _ligne(forme: Ligne) -> str:
    return '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (
        forme.x1, forme.y1, forme.x2, forme.y2, forme.couleur, max(1, forme.epaisseur)
    )


def _ellipse(forme: Ellipse) -> str:
    style = "fill:%s" % (forme.fond if forme.fond else "none")
    if forme.bordure and forme.epaisseur:
        style += ";stroke:%s;stroke-width:%g" % (forme.bordure, forme.epaisseur)
    return '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" style="%s"/>' % (
        forme.x + forme.l / 2, forme.y + forme.h / 2, forme.l / 2, forme.h / 2, style
    )


def _image(forme: Image) -> str:
    return '<image x="%g" y="%g" width="%g" height="%g" preserveAspectRatio="none" href="%s"/>' % (
        forme.x, forme.y, forme.l, forme.h, forme.donnees
    )


_RENDUS = {
    FormeTexte: _forme_texte,
    Forme: _rect,
    Texte: _texte,
    Ligne: _ligne,
    Ellipse: _ellipse,
    Image: _image,
}


def rendre_ecran(ecran: Ecran, fond: bool = True) -> str:
    """Serialise un ecran en document SVG autonome."""
    morceaux = [
        '<svg xmlns="%s" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="%d" height="%d" viewBox="0 0 %d %d">' % (NS_SVG, ecran.largeur, ecran.hauteur, ecran.largeur, ecran.hauteur),
    ]
    if fond:
        morceaux.append(
            '<rect x="0" y="0" width="%d" height="%d" style="fill:%s"/>'
            % (ecran.largeur, ecran.hauteur, ecran.fond)
        )
    for forme in ecran.formes:
        rendu = _RENDUS.get(type(forme))
        if rendu is None:
            raise TypeError("Primitive non rendue : %r" % type(forme).__name__)
        morceaux.append(rendu(forme))
    morceaux.append("</svg>")
    return "".join(morceaux)


def rendre_gallery(ecrans: list[Ecran], colonnes: int = 4) -> str:
    """Planche de contact horizontale : toutes les maquettes cote a cote."""
    if not ecrans:
        return "<html><body></body></html>"
    largeur = ecrans[0].largeur
    hauteur = ecrans[0].hauteur
    marge = 24
    etiquette = 34

    lignes = []
    for debut in range(0, len(ecrans), colonnes):
        lot = ecrans[debut:debut + colonnes]
        cellules = []
        for ecran in lot:
            cellules.append(
                '<figure style="margin:0;display:flex;flex-direction:column;align-items:center;gap:8px;">'
                '<div style="background:#fff;border-radius:10px;overflow:hidden;'
                'box-shadow:0 4px 18px rgba(0,0,0,.14);">%s</div>'
                '<figcaption style="font-family:%s;font-size:12px;color:#5C6B59;text-align:center;">%s</figcaption>'
                "</figure>" % (rendre_ecran(ecran), charte.POLICE, escape(ecran.nom))
            )
        lignes.append(
            '<div style="display:flex;gap:%dpx;justify-content:center;align-items:flex-start;">%s</div>'
            % (marge, "".join(cellules))
        )

    return (
        "<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>CampusShare — planches de maquettes</title></head>"
        '<body style="margin:0;padding:40px 24px;background:#EEF1EE;'
        'font-family:%s;">'
        '<h1 style="text-align:center;font-family:%s;font-size:24px;color:#16210F;margin:0 0 8px;">CampusShare — maquettes</h1>'
        '<p style="text-align:center;font-family:%s;font-size:13px;color:#5C6B59;margin:0 0 36px;">'
        "Application mobile — %d écrans</p>"
        '<div style="display:flex;flex-direction:column;gap:%dpx;">%s</div>'
        "</body></html>"
        % (charte.POLICE, charte.POLICE, charte.POLICE, len(ecrans), etiquette + marge, "".join(lignes))
    )
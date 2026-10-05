"""Metrique de texte : estimation de la largeur et de la hauteur occupiedes.

Utilise par la bibliotheque de composants (pour dimensionner les pastilles et
les puces), par les ecrans (pour reserver la bonne hauteur) et par le linter de
mise en page. Une seule mesure pour tous garantit que les largeurs annoncees
correspondent aux largeurs reellement dessinees.

La police de l'application est sans-serif ; l'estimation repose sur une table
de largeurs relatives par caractere, volontairement simple et stable.
"""

from __future__ import annotations

import re

# Largeur relative d'un caractere, en em (1 em = taille de police).
# Categories usuelles d'une police sans-serif.
_NARRE = set("iljtfrI.,;:'!|[]()")
_LARGE = set("mwMW@%")
_MOYEN = set("abcdeghknopqrsuvxyz0123456789-+=/?")
_MAJUSCULE = set("ABCDEFGHJKLNOPQRSTUVXYZÇÉÈÀ")

# Largeur d'une espace.
_ESPACE = 0.26

_TAILES = re.compile(r"<[^>]+>")


def _largeur_caractere(caractere: str) -> float:
    if caractere == " ":
        return _ESPACE
    if caractere in _NARRE:
        return 0.30
    if caractere in _LARGE:
        return 0.86
    if caractere in _MAJUSCULE:
        return 0.68
    if caractere in _MOYEN:
        return 0.55
    return 0.55


def largeur_texte(contenu: str, taille: float = 14, gras: bool = False) -> float:
    """Largeur estimee d'un fragment de texte, en pixels.

    Le balisage HTML est ignore. Un texte en gras est legerement plus large.
    """
    nu = _TAILES.sub("", contenu)
    nu = nu.replace("&nbsp;", " ").replace("&eacute;", "é")
    total = sum(_largeur_caractere(c) for c in nu)
    # Les caracteres accentues sont sensiblement plus larges.
    total += 0.12 * sum(1 for c in nu if ord(c) > 127)
    facteur = 1.045 if gras else 1.0
    return total * taille * facteur


def nombre_lignes(contenu: str, largeur: float, taille: float = 14, gras: bool = False) -> int:
    """Nombre de lignes apres retour a la ligne automatique.

    Les balises ``<br>`` imposent un saut de ligne. Chaque paragraphe est
    ensuite decoupe pour tenir dans ``largeur``.
    """
    if largeur <= 0:
        return 1
    total = 0
    for paragraphe in contenu.split("<br>"):
        mots = paragraphe.split()
        if not mots:
            total += 1
            continue
        ligne = 0
        lignes = 1
        for mot in mots:
        # Largeur du mot seul, puis avec l'espace qui le precede.
            largeur_mot = largeur_texte(mot, taille, gras)
            largeur_espace = _ESPACE * taille
            if ligne == 0:
                ligne = largeur_mot
            elif ligne + largeur_espace + largeur_mot <= largeur:
                ligne += largeur_espace + largeur_mot
            else:
                lignes += 1
                ligne = largeur_mot
        total += lignes
    return total


def hauteur_texte(
    contenu: str,
    largeur: float,
    taille: float = 14,
    gras: bool = False,
    interligne: float = 1.25,
) -> float:
    """Hauteur estimee du bloc de texte apres retour a la ligne."""
    return nombre_lignes(contenu, largeur, taille, gras) * taille * interligne
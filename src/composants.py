"""Bibliothèque de composants d'interface reutilisables.

Principes d'ecoconception appliques :
  - composants generiques (carte, bouton, champ, badge) reutilises par tous
    les ecrans, ce qui garantit la coherence de la charte de bout en bout ;
  - icones vectorielles tracees a partir de primitives simples plutot que de
    polices d'icones ou de bitmaps ;
  - un seul niveau d'elevation et une seule famille typographique ;
  - cibles tactiles d'au moins 44 px (accessibilite).

Toutes les fonctions prennent des coordonnees absolues : la composition reste
 explicite et lisible dans chaque ecran.
"""

from __future__ import annotations

from . import charte
from .mesure import largeur_texte
from .scene import (
    H_CENTRE,
    H_DROITE,
    V_CENTRE,
    Ellipse,
    Forme,
    FormeTexte,
    Ligne,
    Texte,
)

LARGEUR = charte.LARGEUR_ECRAN
HAUTEUR = charte.HAUTEUR_ECRAN
UTILE = charte.LARGEUR_UTILE
M = charte.MARGE

# Interligne du corps de texte, aligne sur celui du rendu HTML.
INTERLIGNE_CORPS = 1.3


def hauteur_ligne(taille: int, interligne: float = 1.0) -> float:
    """Hauteur occupee par une ligne de texte de la taille donnee."""
    return taille * (interligne if interligne else 1.0)


# ---------------------------------------------------------------------------
# Primitives de trace
# ---------------------------------------------------------------------------


def _polyline(points, couleur: str, epaisseur: float = 2.0, joints: bool = True):
    """Suite de segments (utilisee pour les icones)."""
    segments = []
    for i in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[i], points[i + 1]
        segments.append(Ligne(x1, y1, x2, y2, couleur, epaisseur))
    return segments


def _rect_p(x, y, l, h, couleur, epaisseur=2.0, rayon=0.0):
    """Quatre segments formant un rectangle (contour d'icone)."""
    return _polyline(
        [
            (x + rayon, y),
            (x + l - rayon, y),
            (x + l, y + rayon),
            (x + l, y + h - rayon),
            (x + l - rayon, y + h),
            (x + rayon, y + h),
            (x, y + h - rayon),
            (x, y + rayon),
            (x + rayon, y),
        ],
        couleur,
        epaisseur,
    )


# ---------------------------------------------------------------------------
# Icones (24 x 24, centrees dans la boite donnee)
# ---------------------------------------------------------------------------


def _cadre(cx, cy, taille=22):
    """Boite carree de l'icone, centree sur (cx, cy)."""
    return cx - taille / 2, cy - taille / 2, taille


def icone_accueil(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline([(x, y + t * 0.42), (x + t / 2, y), (x + t, y + t * 0.42)], couleur, 2.2) + _polyline(
        [(x + t * 0.13, y + t * 0.38), (x + t * 0.13, y + t), (x + t * 0.87, y + t), (x + t * 0.87, y + t * 0.38)],
        couleur, 2.2,
    )


def icone_ajouter(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline([(x + t / 2, y + t * 0.18), (x + t / 2, y + t * 0.82)], couleur, 2.4) + _polyline(
        [(x + t * 0.18, y + t / 2), (x + t * 0.82, y + t / 2)], couleur, 2.4
    )


def icone_message(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [
            (x + t * 0.08, y + t * 0.18), (x + t * 0.92, y + t * 0.18),
            (x + t * 0.92, y + t * 0.68), (x + t * 0.34, y + t * 0.68),
            (x + t * 0.12, y + t * 0.9), (x + t * 0.20, y + t * 0.68),
            (x + t * 0.08, y + t * 0.68), (x + t * 0.08, y + t * 0.18),
        ],
        couleur, 2.2,
    )


def icone_profil(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return [Ellipse(x + t * 0.32, y + t * 0.10, t * 0.36, t * 0.36, None, couleur, 2.2)] + _polyline(
        [
            (x + t * 0.10, y + t * 0.95), (x + t * 0.10, y + t * 0.80),
            (x + t * 0.32, y + t * 0.58), (x + t * 0.68, y + t * 0.58),
            (x + t * 0.90, y + t * 0.80), (x + t * 0.90, y + t * 0.95),
        ],
        couleur, 2.2,
    )


def icone_recherche(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return [Ellipse(x + t * 0.08, y + t * 0.08, t * 0.58, t * 0.58, None, couleur, 2.2)] + _polyline(
        [(x + t * 0.62, y + t * 0.62), (x + t * 0.95, y + t * 0.95)], couleur, 2.2
    )


def icone_cloche(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [
            (x + t * 0.22, y + t * 0.72), (x + t * 0.22, y + t * 0.45),
            (x + t * 0.35, y + t * 0.22), (x + t * 0.65, y + t * 0.22),
            (x + t * 0.78, y + t * 0.45), (x + t * 0.78, y + t * 0.72),
            (x + t * 0.92, y + t * 0.80), (x + t * 0.08, y + t * 0.80),
            (x + t * 0.22, y + t * 0.72),
        ],
        couleur, 2.0,
    ) + [Ellipse(x + t * 0.43, y + t * 0.84, t * 0.14, t * 0.14, couleur, None, 0)]


def icone_retour(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [(x + t * 0.85, y + t * 0.5), (x + t * 0.15, y + t * 0.5)], couleur, 2.2
    ) + _polyline([(x + t * 0.45, y + t * 0.2), (x + t * 0.15, y + t * 0.5), (x + t * 0.45, y + t * 0.8)], couleur, 2.2)


def icone_coeur(cx, cy, couleur, taille=22, rempli=False):
    x, y, t = _cadre(cx, cy, taille)
    points = [
        (x + t * 0.5, y + t * 0.88), (x + t * 0.12, y + t * 0.52),
        (x + t * 0.12, y + t * 0.32), (x + t * 0.30, y + t * 0.20),
        (x + t * 0.5, y + t * 0.36), (x + t * 0.70, y + t * 0.20),
        (x + t * 0.88, y + t * 0.32), (x + t * 0.88, y + t * 0.52),
        (x + t * 0.5, y + t * 0.88),
    ]
    return _polyline(points, couleur, 2.0)


def icone_etoile(cx, cy, couleur, taille=14, rempli=True):
    x, y, t = _cadre(cx, cy, taille)
    import math

    pts = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        rayon = t / 2 if i % 2 == 0 else t / 4.4
        pts.append((x + t / 2 + rayon * math.cos(angle), y + t / 2 + rayon * math.sin(angle)))
    return _polyline(pts + [pts[0]], couleur, 1.4)


def icone_agenda(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _rect_p(x + t * 0.08, y + t * 0.18, t * 0.84, t * 0.74, couleur, 2.0, t * 0.08) + _polyline(
        [(x + t * 0.08, y + t * 0.42), (x + t * 0.92, y + t * 0.42)], couleur, 2.0
    ) + _polyline([(x + t * 0.32, y + t * 0.08), (x + t * 0.32, y + t * 0.26)], couleur, 2.0) + _polyline(
        [(x + t * 0.68, y + t * 0.08), (x + t * 0.68, y + t * 0.26)], couleur, 2.0
    )


def icone_appareil(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _rect_p(x + t * 0.26, y + t * 0.06, t * 0.48, t * 0.88, couleur, 2.0, t * 0.06) + _polyline(
        [(x + t * 0.40, y + t * 0.78), (x + t * 0.60, y + t * 0.78)], couleur, 2.0
    )


def icone_livre(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [(x + t * 0.5, y + t * 0.24), (x + t * 0.5, y + t * 0.86)], couleur, 2.0
    ) + _polyline(
        [(x + t * 0.5, y + t * 0.24), (x + t * 0.10, y + t * 0.16), (x + t * 0.10, y + t * 0.76),
         (x + t * 0.5, y + t * 0.86)], couleur, 2.0
    ) + _polyline(
        [(x + t * 0.5, y + t * 0.24), (x + t * 0.90, y + t * 0.16), (x + t * 0.90, y + t * 0.76),
         (x + t * 0.5, y + t * 0.86)], couleur, 2.0
    )


def icone_flacon(cx, cy, couleur, taille=22):
    """Erlenmeyer / verrerie de laboratoire."""
    x, y, t = _cadre(cx, cy, taille)
    return _polyline([(x + t * 0.38, y + t * 0.08), (x + t * 0.38, y + t * 0.36)], couleur, 2.0) + _polyline(
        [(x + t * 0.62, y + t * 0.08), (x + t * 0.62, y + t * 0.36)], couleur, 2.0
    ) + _polyline(
        [(x + t * 0.38, y + t * 0.36), (x + t * 0.14, y + t * 0.88), (x + t * 0.86, y + t * 0.88),
         (x + t * 0.62, y + t * 0.36)], couleur, 2.0
    )


def icone_crayon(cx, cy, couleur, taille=20):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [(x + t * 0.16, y + t * 0.84), (x + t * 0.22, y + t * 0.62), (x + t * 0.66, y + t * 0.18),
         (x + t * 0.86, y + t * 0.38), (x + t * 0.42, y + t * 0.82), (x + t * 0.16, y + t * 0.84)], couleur, 1.9
    )


def icone_poubelle(cx, cy, couleur, taille=20):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline([(x + t * 0.14, y + t * 0.26), (x + t * 0.86, y + t * 0.26)], couleur, 1.9) + _polyline(
        [(x + t * 0.36, y + t * 0.26), (x + t * 0.24, y + t * 0.90)], couleur, 1.9
    ) + _polyline([(x + t * 0.64, y + t * 0.26), (x + t * 0.76, y + t * 0.90)], couleur, 1.9) + _polyline(
        [(x + t * 0.24, y + t * 0.90), (x + t * 0.76, y + t * 0.90)], couleur, 1.9
    ) + _polyline([(x + t * 0.36, y + t * 0.26), (x + t * 0.38, y + t * 0.10)], couleur, 1.9) + _polyline(
        [(x + t * 0.64, y + t * 0.26), (x + t * 0.62, y + t * 0.10)], couleur, 1.9
    ) + _polyline([(x + t * 0.38, y + t * 0.10), (x + t * 0.62, y + t * 0.10)], couleur, 1.9)


def icone_camera(cx, cy, couleur, taille=24):
    x, y, t = _cadre(cx, cy, taille)
    return _rect_p(x, y + t * 0.22, t, t * 0.68, couleur, 2.0, t * 0.10) + _polyline(
        [(x + t * 0.32, y + t * 0.22), (x + t * 0.38, y + t * 0.10), (x + t * 0.62, y + t * 0.10),
         (x + t * 0.68, y + t * 0.22)], couleur, 2.0
    ) + [Ellipse(x + t * 0.33, y + t * 0.40, t * 0.34, t * 0.34, None, couleur, 2.0)]


def icone_coche(cx, cy, couleur, taille=20):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline([(x + t * 0.14, y + t * 0.52), (x + t * 0.42, y + t * 0.80), (x + t * 0.88, y + t * 0.20)], couleur, 2.4)


def icone_fermeture(cx, cy, couleur, taille=20):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline([(x + t * 0.15, y + t * 0.15), (x + t * 0.85, y + t * 0.85)], couleur, 2.2) + _polyline(
        [(x + t * 0.85, y + t * 0.15), (x + t * 0.15, y + t * 0.85)], couleur, 2.2
    )


def icone_oeil(cx, cy, couleur, taille=22):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [(x + t * 0.04, y + t * 0.5), (x + t * 0.26, y + t * 0.24), (x + t * 0.5, y + t * 0.16),
         (x + t * 0.74, y + t * 0.24), (x + t * 0.96, y + t * 0.5)], couleur, 2.0
    ) + _polyline(
        [(x + t * 0.04, y + t * 0.5), (x + t * 0.26, y + t * 0.76), (x + t * 0.5, y + t * 0.84),
         (x + t * 0.74, y + t * 0.76), (x + t * 0.96, y + t * 0.5)], couleur, 2.0
    ) + [Ellipse(x + t * 0.38, y + t * 0.38, t * 0.24, t * 0.24, couleur, None, 0)]


def icone_localisation(cx, cy, couleur, taille=18):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [(x + t * 0.5, y + t * 0.94), (x + t * 0.16, y + t * 0.50), (x + t * 0.24, y + t * 0.14),
         (x + t * 0.5, y + t * 0.06), (x + t * 0.76, y + t * 0.14), (x + t * 0.84, y + t * 0.50),
         (x + t * 0.5, y + t * 0.94)], couleur, 1.9
    ) + [Ellipse(x + t * 0.36, y + t * 0.30, t * 0.28, t * 0.28, None, couleur, 1.9)]


def icone_batiment(cx, cy, couleur, taille=18):
    x, y, t = _cadre(cx, cy, taille)
    return _polyline(
        [(x + t * 0.10, y + t * 0.92), (x + t * 0.10, y + t * 0.26), (x + t * 0.5, y + t * 0.06),
         (x + t * 0.90, y + t * 0.26), (x + t * 0.90, y + t * 0.92)], couleur, 1.9
    ) + _polyline([(x + t * 0.10, y + t * 0.92), (x + t * 0.90, y + t * 0.92)], couleur, 1.9)


def icone_horloge(cx, cy, couleur, taille=16):
    x, y, t = _cadre(cx, cy, taille)
    return [Ellipse(x, y, t, t, None, couleur, 1.8)] + _polyline(
        [(x + t / 2, y + t * 0.26), (x + t / 2, y + t / 2), (x + t * 0.72, y + t * 0.60)], couleur, 1.8
    )


def icone_deconnexion(cx, cy, couleur, taille=18):
    x, y, t = _cadre(cx, cy, taille)
    return _rect_p(x + t * 0.06, y + t * 0.14, t * 0.56, t * 0.72, couleur, 1.9, t * 0.10) + _polyline(
        [(x + t * 0.62, y + t * 0.5), (x + t * 0.98, y + t * 0.5)], couleur, 1.9
    ) + _polyline(
        [(x + t * 0.80, y + t * 0.32), (x + t * 0.98, y + t * 0.5), (x + t * 0.80, y + t * 0.68)], couleur, 1.9
    )


# ---------------------------------------------------------------------------
# Logo
# ---------------------------------------------------------------------------


def logo(cx, cy, taille=40, couleur=charte.VERT, accent=charte.ORANGE):
    """Logo CampusShare : deux mains stylisees formant un 'C' partage.

    Ronde : une forme circulaire verte, deux chevrons oranges en vis-a-vis qui
    suggerent l'echange, et un point central de partage.
    """
    d = taille
    x = cx - d / 2
    y = cy - d / 2
    morceaux = [
        Ellipse(x, y, d, d, couleur, None, 0, nom="Logo / pastille"),
    ]
    # deux chevrons en echange
    morceaux += _polyline(
        [(cx - d * 0.26, cy - d * 0.16), (cx - d * 0.06, cy), (cx - d * 0.26, cy + d * 0.16)],
        accent, d * 0.075,
    )
    morceaux += _polyline(
        [(cx + d * 0.26, cy - d * 0.16), (cx + d * 0.06, cy), (cx + d * 0.26, cy + d * 0.16)],
        accent, d * 0.075,
    )
    morceaux.append(Forme(cx - d * 0.035, cy + d * 0.26, d * 0.07, d * 0.07, accent, d * 0.035, nom="Logo / partage"))
    return morceaux


def logo_clair(cx, cy, taille=28):
    """Variante monochrome claire du logo, pour fond vert."""
    d = taille
    x = cx - d / 2
    y = cy - d / 2
    morceaux = _polyline(
        [(cx - d * 0.28, cy - d * 0.20), (cx - d * 0.06, cy), (cx - d * 0.28, cy + d * 0.20)],
        "#FFFFFF", d * 0.085,
    )
    morceaux += _polyline(
        [(cx + d * 0.28, cy - d * 0.20), (cx + d * 0.06, cy), (cx + d * 0.28, cy + d * 0.20)],
        "#FFFFFF", d * 0.085,
    )
    morceaux.append(Forme(cx - d * 0.04, cy + d * 0.30, d * 0.08, d * 0.08, "#FFFFFF", d * 0.04))
    return morceaux


# ---------------------------------------------------------------------------
# Chrome systeme
# ---------------------------------------------------------------------------


def barre_etat(couleur: str = "#16210F", heure: str = "9:41") -> list:
    """Barre d'etat systeme (repere de lisibilite, non interactive)."""
    morceaux = []
    for i, largeur in enumerate((3, 4, 5, 6)):
        morceaux.append(Forme(20 + i * 5, 15 - largeur, 3, largeur, couleur, 0.8))
    morceaux.append(Texte(52, 6, 60, heure, charte.T_LABEL, True, couleur))
    # indicateur de batterie
    morceaux.append(Forme(LARGEUR - 32, 8, 20, 10, None, 2, couleur, 1))
    morceaux.append(Forme(LARGEUR - 30, 10, 12, 6, couleur, 0))
    morceaux.append(Forme(LARGEUR - 10, 11, 2, 4, couleur, 1))
    # Wi-Fi : trois arcs simules par des segments
    morceaux += _polyline([(LARGEUR - 62, 12), (LARGEUR - 56, 9), (LARGEUR - 50, 12)], couleur, 1.6)
    morceaux += _polyline([(LARGEUR - 59, 14.5), (LARGEUR - 56, 12.5), (LARGEUR - 53, 14.5)], couleur, 1.6)
    morceaux.append(Ellipse(LARGEUR - 57.4, 16.4, 2.8, 2.8, couleur, None, 0))
    return morceaux


def barre_onglets(actif: str = "accueil") -> list:
    """Barre d'onglets inferieure : 4 destinations, cible tactile 44 px."""
    hauteur = charte.BARRE_ONGLETS
    y = HAUTEUR - hauteur
    morceaux = [
        Forme(0, y, LARGEUR, hauteur, charte.SURFACE, 0, nom="Onglets / fond"),
        Ligne(0, y, LARGEUR, y, charte.BORDURE, 1),
    ]
    destinations = [
        ("accueil", "Accueil", icone_accueil),
        ("publier", "Publier", icone_ajouter),
        ("messages", "Messages", icone_message),
        ("profil", "Profil", icone_profil),
    ]
    largeur_case = LARGEUR / len(destinations)
    for i, (cle, libelle, ico) in enumerate(destinations):
        cx = largeur_case * (i + 0.5)
        selectionne = cle == actif
        couleur = charte.VERT if selectionne else charte.TEXTE_DISCRET
        if cle == "publier":
            # Le bouton central « Publier » est mis en avant : pastille pleine.
            r = 21
            morceaux.append(Ellipse(cx - r, y + 10, r * 2, r * 2, charte.VERT if not selectionne else charte.VERT_FONCE, None, 0))
            morceaux += ico(cx, y + 21, "#FFFFFF", 20)
        else:
            morceaux += ico(cx, y + 21, couleur, 21)
            if selectionne:
                morceaux.append(Forme(cx - 4, y + 40, 8, 3, charte.VERT, 1.5))
        morceaux.append(
            Texte(cx - largeur_case / 2, y + 46, largeur_case, libelle, 10, selectionne, couleur, H_CENTRE)
        )
    return morceaux


# ---------------------------------------------------------------------------
# Composants
# ---------------------------------------------------------------------------


def bouton(x, y, l, texte, h=charte.BOUTON_H, variante="primaire", taille=None) -> FormeTexte:
    """Bouton d'action. Variantes : primaire, secondaire, discret, danger."""
    if variante == "primaire":
        fond, couleur, bordure, epaisseur = charte.VERT, "#FFFFFF", None, 0
    elif variante == "accent":
        fond, couleur, bordure, epaisseur = charte.ORANGE, charte.TEXTE_SUR_ACCENT, None, 0
    elif variante == "secondaire":
        fond, couleur, bordure, epaisseur = charte.SURFACE, charte.VERT, charte.VERT, 1
    elif variante == "discret":
        fond, couleur, bordure, epaisseur = charte.SURFACE, charte.TEXTE_SECONDAIRE, charte.BORDURE, 1
    elif variante == "danger":
        fond, couleur, bordure, epaisseur = charte.SURFACE, charte.ALERTE, "#F0C9C9", 1
    else:
        raise ValueError("Variante de bouton inconnue : %r" % variante)
    return FormeTexte(
        x, y, l, h, texte,
        taille or charte.T_BOUTON, True,
        fond, couleur, H_CENTRE, V_CENTRE,
        charte.RAYON_BOUTON, bordure, epaisseur,
    )


def champ(x, y, l, etiquette, valeur="", h=charte.CHAMP_H, aide=None, icone=None) -> list:
    """Champ de formulaire : etiquette au-dessus, cadre, valeur ou invite.

    Retourne la liste des primitives. ``y`` est mis a jour dans l'appelant pour
    empiler les champs ; a titre indicatif le cadre occupe
    ``hauteur_totale(y)`` pixels.
    """
    morceaux = []
    if etiquette:
        morceaux.append(Texte(x, y, l, etiquette, charte.T_LABEL, True, charte.TEXTE_SECONDAIRE))
        y += hauteur_ligne(charte.T_LABEL) + charte.ESP_1
    morceaux.append(Forme(x, y, l, h, charte.SURFACE, charte.RAYON_CHAMP, charte.BORDURE_FORCE, 1, nom="Champ / cadre"))
    decalage = 14
    if icone:
        morceaux += icone(x + 20, y + h / 2, charte.TEXTE_DISCRET, 18)
        decalage = 32
    hauteur_texte = hauteur_ligne(charte.T_CORPS, INTERLIGNE_CORPS)
    if valeur:
        morceaux.append(Texte(x + decalage, y + (h - hauteur_texte) / 2,
                              l - decalage - 14, valeur, charte.T_CORPS, False, charte.TEXTE))
    if aide:
        morceaux.append(Texte(x, y + h + 6, l, aide, charte.T_CAPTION, False, charte.TEXTE_DISCRET))
    return morceaux


def hauteur_champ(etiquette: bool, aide: bool = False, h: int = charte.CHAMP_H) -> float:
    """Hauteur totale occupee par un champ, etiquette et aide comprises."""
    total = float(h)
    if etiquette:
        total += hauteur_ligne(charte.T_LABEL) + charte.ESP_1
    if aide:
        total += hauteur_ligne(charte.T_CAPTION) + 6
    return total


def case_a_cocher(x, y, coche=True, l=22) -> list:
    """Case a cocher carree de 22 px ; la cible tactile est assuree par le label."""
    if coche:
        return [
            Forme(x, y, l, l, charte.VERT, 5, None, 0),
            *icone_coche(x + l / 2, y + l / 2, "#FFFFFF", 14),
        ]
    return [Forme(x, y, l, l, charte.SURFACE, 5, charte.BORDURE_FORCE, 1.5)]


def badge(x, y, texte, fond=charte.VERT_CLAIR, couleur=charte.VERT, taille=charte.T_CAPTION, h=22, pad=10) -> FormeTexte:
    """Pastille d'etat (texte court). Role informatif, pas une cible tactile."""
    largeur = max(largeur_texte(texte, taille, True) + 2 * pad, h + 8)
    return FormeTexte(x, y, largeur, h, texte, taille, True, fond, couleur,
                      H_CENTRE, V_CENTRE, h / 2, None, 0,
                      role="badge", nom="Badge")


def separateur(y, couleur=charte.BORDURE, epaisseur=1) -> Ligne:
    return Ligne(0, y, LARGEUR, y, couleur, epaisseur)


def separateur_marge(y, couleur=charte.BORDURE) -> Ligne:
    return Ligne(M, y, LARGEUR - M, y, couleur, 1)


def avatar(x, y, d, initiales, fond=charte.VERT_CLAIR, couleur=charte.VERT, taille=None) -> list:
    """Avatar : pastille coloree portant des initiales."""
    taille = taille or int(d * 0.40)
    return [
        Ellipse(x, y, d, d, fond, None, 0, nom="Avatar / fond"),
        Texte(x, y + (d - taille * 1.25) / 2, d, initiales, taille, True, couleur, H_CENTRE),
    ]


def notation(note: float, x, y, taille=13, couleur=charte.ORANGE_FONCE) -> list:
    """Note sur 5, passee sous forme d'etoile suivie de la valeur."""
    morceaux = [*icone_etoile(x + 7, y + 7, couleur, 13)]
    morceaux.append(Texte(x + 18, y - 1, 60, "%.1f/5" % note, taille, True, charte.TEXTE))
    return morceaux


def vignette(x, y, l, h, teinte=charte.VIGNETTE, icone=None) -> list:
    """Zone d'image sans visuel : fond neutre + icone centree (placeholder)."""
    morceaux = [Forme(x, y, l, h, teinte, 8, None, 0)]
    if icone:
        morceaux += icone(x + l / 2, y + h / 2, "#A9B5A5", min(l, h) * 0.42)
    return morceaux


def barre_recherche(x, y, l, invite="Rechercher un objet...", h=42) -> list:
    """Barre de recherche : capsule avec icone loupe."""
    morceaux = [
        Forme(x, y, l, h, "#EDF1ED", h / 2, None, 0, nom="Recherche / fond"),
        *icone_recherche(x + 22, y + h / 2, charte.TEXTE_DISCRET, 17),
        Texte(x + 38, y + (h - charte.T_CORPS * 1.3) / 2, l - 48, invite, charte.T_CORPS, False, charte.TEXTE_DISCRET),
    ]
    return morceaux


def puce_filtre(x, y, texte, actif=False, h=32, pad=14) -> FormeTexte:
    """Puce de filtre horizontale. Cible tactile de 32 px, zone elargie a 44 px."""
    largeur = largeur_texte(texte, charte.T_LABEL, True) + 2 * pad
    if actif:
        return FormeTexte(x, y, largeur, h, texte, charte.T_LABEL, True,
                          charte.VERT, "#FFFFFF", H_CENTRE, V_CENTRE, h / 2, None, 0,
                          role="puce", nom="Puce / %s" % texte)
    return FormeTexte(x, y, largeur, h, texte, charte.T_LABEL, False,
                      charte.SURFACE, charte.TEXTE_SECONDAIRE, H_CENTRE, V_CENTRE, h / 2,
                      charte.BORDURE, 1, role="puce", nom="Puce / %s" % texte)


def rangee_puces(x, y, largeur_max, libelles, actif=0, ecran=8, h=32, pad=14):
    """Pose une rangee de puces de filtre en place.

    Retourne (formes, largeur_utilisee, tronquee). Les puces qui ne tiennent pas
    dans ``largeur_max`` sont omises et ``tronquee`` vaut True : la maquette ne
    dessine jamais de contenu hors du cadre de l'ecran.
    """
    formes = []
    curseur = x
    for i, libelle in enumerate(libelles):
        puce = puce_filtre(0, y, libelle, actif=i == actif, h=h, pad=pad)
        if curseur + puce.l > x + largeur_max + 0.5:
            return formes, curseur - x, True
        puce.x = curseur
        formes.append(puce)
        curseur += puce.l + ecran
    return formes, curseur - x - (ecran if formes else 0), False


def entete_onglets(x, y, libelles, actif=0, l=None, h=40) -> list:
    """Segmentation d'onglets (2 onglets max, style underline)."""
    l = l or charte.LARGEUR_UTILE
    largeur_case = l / len(libelles)
    morceaux = [Ligne(x, y + h, x + l, y + h, charte.BORDURE, 1)]
    for i, libelle in enumerate(libelles):
        cx = x + largeur_case * i
        selectionne = i == actif
        morceaux.append(
            Texte(cx, y + 12, largeur_case, libelle, 14, selectionne,
                  charte.TEXTE if selectionne else charte.TEXTE_DISCRET, H_CENTRE)
        )
        if selectionne:
            morceaux.append(Forme(cx + largeur_case * 0.28, y + h - 3, largeur_case * 0.44, 3, charte.VERT, 1.5))
    return morceaux


def barre_action_fixe(y, contenu) -> list:
    """Barre d'action fixe en bas d'ecran, avec bordure haute."""
    return [
        Forme(0, y, LARGEUR, HAUTEUR - y, charte.SURFACE, 0, nom="Action / fond"),
        Ligne(0, y, LARGEUR, y, charte.BORDURE, 1),
    ] + list(contenu)


def carte(x, y, l, h, contenu=None, rayon=charte.RAYON_CARTE) -> Forme:
    """Carte de contenu : surface blanche, coins arrondis, bordure discrete."""
    return Forme(x, y, l, h, charte.SURFACE, rayon, charte.BORDURE, 1, nom="Carte")


def message_info(x, y, l, texte, fond=charte.VERT_CLAIR, bordure=charte.VERT_CLAIR,
                 couleur=charte.VERT, icone=None, h=None) -> list:
    """Encart d'information (regles eco-responsables, confirmations)."""
    taille = charte.T_LABEL
    hauteur = h or (taille * 1.4 * (1 + texte.count("<br>")) + 2 * charte.ESP_3)
    morceaux = [Forme(x, y, l, hauteur, fond, 10, bordure, 1, nom="Encart")]
    decalage = charte.ESP_3
    if icone:
        morceaux += icone(x + 18, y + 18, couleur, 16)
        decalage = 36
    morceaux.append(
        Texte(x + decalage, y + charte.ESP_2, l - decalage - charte.ESP_3, texte, taille, False, couleur)
    )
    return morceaux


def icone_chevron(cx, cy, couleur, taille=18, vers="bas"):
    """Chevron de deroulement pour les selecteurs."""
    x, y, t = _cadre(cx, cy, taille)
    if vers == "haut":
        return _polyline([(x + t * 0.18, y + t * 0.62), (x + t * 0.5, y + t * 0.30), (x + t * 0.82, y + t * 0.62)], couleur, 2.0)
    if vers == "gauche":
        return _polyline([(x + t * 0.62, y + t * 0.18), (x + t * 0.30, y + t * 0.5), (x + t * 0.62, y + t * 0.82)], couleur, 2.0)
    return _polyline([(x + t * 0.18, y + t * 0.38), (x + t * 0.5, y + t * 0.70), (x + t * 0.82, y + t * 0.38)], couleur, 2.0)


def champ_selecteur(x, y, l, etiquette, valeur, h=charte.CHAMP_H, icone=None) -> list:
    """Champ de selection : aspect d'un champ, valeur affichee + chevron.

    ``icone`` place une icone a gauche de la valeur (calendrier, etc.).
    """
    morceaux = []
    if etiquette:
        morceaux.append(Texte(x, y, l, etiquette, charte.T_LABEL, True, charte.TEXTE_SECONDAIRE))
        y += hauteur_ligne(charte.T_LABEL) + charte.ESP_1
    morceaux.append(Forme(x, y, l, h, charte.SURFACE, charte.RAYON_CHAMP, charte.BORDURE_FORCE, 1,
                           nom="Sélecteur / cadre"))
    hauteur_texte = hauteur_ligne(charte.T_CORPS, INTERLIGNE_CORPS)
    decalage = 14
    if icone:
        morceaux += icone(x + 19, y + h / 2, charte.TEXTE_DISCRET, 17)
        decalage = 36
    morceaux.append(Texte(x + decalage, y + (h - hauteur_texte) / 2, l - decalage - 30, valeur,
                          charte.T_CORPS, False, charte.TEXTE))
    morceaux += icone_chevron(x + l - 20, y + h / 2, charte.TEXTE_DISCRET, 16)
    return morceaux


def zone_texte(x, y, l, etiquette, valeur="", h=96) -> list:
    """Zone de saisie multiligne."""
    morceaux = []
    if etiquette:
        morceaux.append(Texte(x, y, l, etiquette, charte.T_LABEL, True, charte.TEXTE_SECONDAIRE))
        y += hauteur_ligne(charte.T_LABEL) + charte.ESP_1
    morceaux.append(Forme(x, y, l, h, charte.SURFACE, charte.RAYON_CHAMP, charte.BORDURE_FORCE, 1,
                           nom="Zone de texte / cadre"))
    hauteur_texte = hauteur_ligne(charte.T_CORPS, INTERLIGNE_CORPS)
    if valeur:
        morceaux.append(Texte(x + 14, y + 12, l - 28, valeur, charte.T_CORPS, False,
                              charte.TEXTE, hauteur=h - 20))
    return morceaux


def bloc_ligne_info(x, y, l, etiquette, valeur, icone=None) -> list:
    """Ligne d'information : icone + etiquette a gauche, valeur a droite."""
    morceaux = []
    if icone:
        morceaux += icone(x + 8, y + 8, charte.TEXTE_DISCRET, 16)
        decalage = 26
    else:
        decalage = 0
    morceaux.append(Texte(x + decalage, y, l * 0.55, etiquette, charte.T_LABEL, False, charte.TEXTE_SECONDAIRE))
    morceaux.append(Texte(x + l * 0.45, y, l * 0.55, valeur, charte.T_LABEL, True, charte.TEXTE, H_DROITE))
    return morceaux


# ---------------------------------------------------------------------------
# Cartes objet
# ---------------------------------------------------------------------------

# Illustration par categorie, choisie dans le jeu d'icones existant : le
# placeholder reste sobre et cohesif avec le reste de l'interface.
_VISUEL = {
    "Technologie": icone_appareil,
    "Livres": icone_livre,
    "Laboratoire": icone_flacon,
    "Sport": icone_coeur,
}


def visuel(categorie: str):
    """Icone d'illustration correspondant a une categorie."""
    return _VISUEL.get(categorie, icone_appareil)


def etiquette_etat(objet) -> FormeTexte:
    """Pastille d'etat : verte si disponible, orange si emprunte."""
    if objet.disponible:
        return badge(0, 0, "Disponible", charte.VERT_CLAIR, charte.VERT)
    return badge(0, 0, "Emprunté", charte.ORANGE_CLAIR, charte.ORANGE_FONCE)


def carte_objet(x, y, l, objet, hauteur=190) -> list:
    """Carte du fil d'actualite (grille 2 colonnes) : visuel, titre, etat,
    proprietaire."""
    morceaux = [carte(x, y, l, hauteur)]
    morceaux += vignette(x + 8, y + 8, l - 16, 86, charte.VIGNETTE, visuel(objet.categorie))

    etiquette = etiquette_etat(objet)
    morceaux.append(
        FormeTexte(x + 10, y + 102, etiquette.l, etiquette.h, etiquette.contenu,
                   etiquette.taille, etiquette.gras, etiquette.fond, etiquette.couleur_texte,
                   H_CENTRE, V_CENTRE, etiquette.rayon, None, 0)
    )

    hauteur_titre = hauteur_ligne(13, 1.25) * 2
    morceaux.append(
        Texte(x + 10, y + 126, l - 20, objet.titre, 13, True, charte.TEXTE,
              hauteur=hauteur_titre)
    )

    # Ligne proprietaire : pastille d'initiales + prenom.
    morceaux += avatar(x + 10, y + hauteur - 32, 20, objet.proprietaire.initiales,
                       charte.VERT_CLAIR, charte.VERT, 9)
    morceaux.append(
        Texte(x + 36, y + hauteur - 29, l - 46,
              "par %s" % objet.proprietaire.nom, 11, False, charte.TEXTE_DISCRET)
    )
    return morceaux


def carte_objet_ligne(x, y, l, objet, hauteur=96, actions=True) -> list:
    """Carte horizontale (liste « Mes annonces ») avec actions rapides."""
    morceaux = [carte(x, y, l, hauteur)]
    morceaux += vignette(x + 10, y + 10, 76, hauteur - 20, charte.VIGNETTE, visuel(objet.categorie))

    largeur_texte = l - 20 - 76 - 12 - (58 if actions else 0)
    morceaux.append(
        Texte(x + 98, y + 14, largeur_texte, objet.titre, 14, True, charte.TEXTE,
              hauteur=hauteur_ligne(14, 1.25) * 2)
    )
    etiquette = etiquette_etat(objet)
    morceaux.append(
        FormeTexte(x + 98, y + 46, etiquette.l, etiquette.h, etiquette.contenu,
                   etiquette.taille, etiquette.gras, etiquette.fond, etiquette.couleur_texte,
                   H_CENTRE, V_CENTRE, etiquette.rayon, None, 0)
    )
    morceaux.append(
        Texte(x + 98, y + 74, largeur_texte, objet.batiment, 11, False, charte.TEXTE_DISCRET)
    )

    if actions:
        # Actions rapides : icons seulement, cible tactile 44 px.
        cx = x + l - 26
        morceaux += icone_crayon(cx, y + hauteur / 2 - 11, charte.TEXTE_SECONDAIRE, 18)
        morceaux += icone_poubelle(cx, y + hauteur / 2 + 13, charte.ALERTE, 18)
    return morceaux
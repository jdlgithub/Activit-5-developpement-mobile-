"""Charte graphique et design tokens du projet CampusShare.

Source unique de verite pour toutes les maquettes : couleurs, typographie,
grille d'espacement et dimensions de l'ecran mobile.

Principes d'ecoconception appliques :
  - palette reduite et semantique (primaire / accent / neutres / etats) ;
  - contraste eleve pour la lisibilite en fort eclairage ;
  - un seul niveau d'elevation (ombre discrete) plutot que des decorations ;
  - une seule famille typographique sans-serif ;
  - rayons et espacements issus d'une echelle reguliere (multiples de 4).
"""

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

# Vert eco-responsable : couleur primaire de la marque.
VERT = "#2E7D32"
VERT_FONCE = "#1B5E20"
VERT_CLAIR = "#E8F5E9"

# Orange doux : accent, utilise avec parcimonie (badges, etats, CTA secondaire).
ORANGE = "#FFB300"
ORANGE_CLAIR = "#FFF3D0"
ORANGE_FONCE = "#8A6100"  # version assombrie pour le texte sur fond clair

# Neutres et fonds.
FOND = "#F4F6F4"
SURFACE = "#FFFFFF"
BORDURE = "#DFE4DF"
BORDURE_FORCE = "#C3CCC3"

# Texte. Contraste eleve sur fond clair.
TEXTE = "#16210F"
TEXTE_SECONDAIRE = "#5C6B59"
TEXTE_DISCRET = "#8A9787"
TEXTE_INVERSE = "#FFFFFF"
TEXTE_SUR_PRIMAIRE = "#FFFFFF"
TEXTE_SUR_ACCENT = "#3D2C00"

# Etats.
SUCCES = "#2E7D32"
ALERTE = "#C62828"
INFO = "#1976D2"

# Degrades de confiance (score de confiance / notes).
CONFIANCE_HAUTE = VERT
CONFIANCE_MOYENNE = ORANGE_FONCE
CONFIANCE_BASSE = ALERTE

# Couleur de fond des vignettes d'illustration (quand aucune image n'est
# disponible) : gris tres clair dans la famille du vert.
VIGNETTE = "#E9EEE9"


# ---------------------------------------------------------------------------
# Typographie
# ---------------------------------------------------------------------------

# Police unique sans-serif, avec replis pour le rendu des apercus.
POLICE = "Roboto, 'Noto Sans', 'DejaVu Sans', sans-serif"

# Echelle typographique. Les tailles sont exprimees en px.
T_EYEBROW = 11  # sur-titre en capitales
T_CAPTION = 11  # legende, meta-information
T_LABEL = 13  # etiquette de champ, texte secondaire
T_CORPS = 14  # corps de texte standard
T_CORPS_FORT = 14  # corps de texte en gras
T_BOUTON = 15  # libelle de bouton
T_SOUS_TITRE = 16  # sous-titre de bloc
T_TITRE_SECTION = 18  # titre de carte / section
T_TITRE = 22  # titre d'ecran
T_ACCUEIL = 30  # Splash uniquement

# Graisse : seule la graisse "bold" est utilisee, ce qui limite le nombre de
# rendu et ameliore la densite visuelle.
POIDS_NORMAL = "normal"
POIDS_GRAS = "bold"


# ---------------------------------------------------------------------------
# Grille et espacement (multiples de 4)
# ---------------------------------------------------------------------------

M = 4
ESP_1 = 4
ESP_2 = 8
ESP_3 = 12
ESP_4 = 16
ESP_5 = 20
ESP_6 = 24
ESP_8 = 32
ESP_10 = 40

# Marges laterales de l'ecran.
MARGE = 20

# Hauteur de la barre d'etat systeme (reperes de contraste en maquette).
BARRE_ETAT = 24

# Hauteur de la barre d'etat applicative.
BARRE_APP = 56

# Hauteur de la barre d'onglets inferieure.
BARRE_ONGLETS = 60

# Hauteur de la barre d'action fixe en bas d'un ecran.
BARRE_ACTION = 72

# Hauteur des elements de formulaire.
CHAMP_H = 48
BOUTON_H = 48


# ---------------------------------------------------------------------------
# Formes
# ---------------------------------------------------------------------------

RAYON_CARTE = 12
RAYON_CHAMP = 10
RAYON_PUCE = 14
RAYON_BOUTON = 10
RAYON_CERCLE = 999

# Epaisseur de bordure unique.
EPAISSEUR_BORDURE = 1

# Ombre unique, tres discrete : un seul niveau d'elevation dans toute l'app.
OMBRE_CARTE = (0, 2, 8, "rgba(22, 33, 15, 0.10)")


# ---------------------------------------------------------------------------
# Cibles tactiles : accesibilite mobile
# ---------------------------------------------------------------------------

# Taille minimale d'une cible tactile (recommandation 44 px).
CIBLE_MIN = 44


# ---------------------------------------------------------------------------
# Ecran de reference
# ---------------------------------------------------------------------------

# Mobile standard en portrait (unite de conception px).
LARGEUR_ECRAN = 360
HAUTEUR_ECRAN = 800

# Largeur utile = ecran - 2 marges laterales.
LARGEUR_UTILE = LARGEUR_ECRAN - 2 * MARGE  # 320


# ---------------------------------------------------------------------------
# Conversion de couleurs vers le format attendu par Pencil (#RRGGBBAA)
# ---------------------------------------------------------------------------


def avec_alpha(couleur: str, alpha: float = 1.0) -> str:
    """Convertit "#RRGGBB" vers "#RRGGBBAA", format natif de Pencil."""
    hexa = couleur.lstrip("#").upper()
    if len(hexa) == 8:
        return "#" + hexa
    if len(hexa) != 6:
        raise ValueError("Couleur hexadecimale invalide : %r" % couleur)
    return "#%s%02X" % (hexa, round(max(0.0, min(1.0, alpha)) * 255))
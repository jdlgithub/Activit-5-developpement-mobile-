"""Donnees d'exemple des maquettes CampusShare.

Centraliser le contenu permet de garder les ecrans coherents entre eux :
un meme objet apparait dans le fil d'actualite, sur sa fiche et dans le
formulaire de demande ; un meme etudiant apparait comme proprietaire et
comme auteur de ses annonces.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Etudiant:
    initiales: str
    nom: str
    filiere: str
    niveau: str
    note: float
    nb_echanges: int

    @property
    def identite(self) -> str:
        return "%s %s" % (self.prenom, self.nom)


@dataclass(frozen=True)
class Objet:
    titre: str
    categorie: str
    etat: str  # "Disponible" ou "Emprunté jusqu'au ..."
    disponible: bool
    proprietaire: Etudiant
    batiment: str
    duree: str  # duree habituelle de pret
    note: float
    description: str
    conditions: tuple[str, ...] = field(default=())
    visuel: str = ""  # indice d'illustration (categorie)
    prix: str = ""


# ---------------------------------------------------------------------------
# Categories (libelles exacts de la maquette)
# ---------------------------------------------------------------------------

CATEGORIES = ("Tous", "Livres", "Technologie", "Laboratoire", "Sport")

# ---------------------------------------------------------------------------
# Etudiants
# ---------------------------------------------------------------------------

SARAH = Etudiant("SK", "Sarah K.", "Informatique", "L3", 4.8, 12)
YASSINE = Etudiant("YB", "Yassine B.", "Génie civil", "Master 1", 4.6, 8)
LINA = Etudiant("LH", "Lina H.", "Biologie", "L2", 4.9, 15)
MEHDI = Etudiant("MB", "Mehdi B.", "Physique", "L1", 4.5, 5)
AWA = Etudiant("AD", "Awa D.", "Mathématiques", "L3", 4.7, 10)

MOI = Etudiant("JA", "Julien A.", "Informatique", "Master 1", 4.9, 21)


# ---------------------------------------------------------------------------
# Objets du fil d'actualite
# ---------------------------------------------------------------------------

OBJETS = (
    Objet(
        titre="Projecteur Epson EB-2150",
        categorie="Technologie",
        etat="Disponible",
        disponible=True,
        proprietaire=SARAH,
        batiment="Bâtiment A · Salle 204",
        duree="Jusqu'à 5 jours",
        note=4.8,
        description=(
            "Projecteur WXGA de 3200 lumens, idéal pour les présentations de "
            "projet et les cours en amphithéâtre. Livré avec un sac de "
            "transport, un câble HDMI et la télécommande."
        ),
        conditions=(
            "Restitution dans le local du département",
            "Nettoyage du filtre à projection avant restitution",
            "Prévoir une marge de 15 min pour l'installation",
        ),
        visuel="projecteur",
    ),
    Objet(
        titre="Manuel d'algèbre linéaire — 4e éd.",
        categorie="Livres",
        etat="Disponible",
        disponible=True,
        proprietaire=AWA,
        batiment="Bibliothèque · Maths",
        duree="Jusqu'à 3 semaines",
        note=4.7,
        description=(
            "Manuel complet avec exercices corrigés, très utilisé pour le "
            "module d'algèbre linéaire (L2 et L3). État général, quelques "
            "marges annotées au crayon."
        ),
        conditions=(
            "Pas de marque-page collé",
            "Retour dans la BU Aristotle",
        ),
        visuel="livre",
    ),
    Objet(
        titre="Multimètre numérique Fluke 117",
        categorie="Laboratoire",
        etat="Emprunté jusqu'au 14 nov.",
        disponible=False,
        proprietaire=MEHDI,
        batiment="Bâtiment C · Labo Physique 2",
        duree="Jusqu'à 2 jours",
        note=4.5,
        description=(
            "Multimètre true RMS catégorie III, indispensable pour les TP "
            "d'électrotechnique. Câbles et pinces fournis."
        ),
        conditions=("Après chaque TP : ranger les sondes",),
        visuel="multimetre",
    ),
    Objet(
        titre="Raquettes de badminton (x2)",
        categorie="Sport",
        etat="Disponible",
        disponible=True,
        proprietaire=LINA,
        batiment="Gymnase · Diderot",
        duree="Jusqu'à 2 semaines",
        note=4.9,
        description=(
            "Paire de raquettes allégères avec housses et volants de rechange. "
            "Idéales pour les séances de badminton du SUDE."
        ),
        conditions=("Renvoyer les raquettes en bon état",),
        visuel="sport",
    ),
    Objet(
        titre="Caméra reflex Canon 200D",
        categorie="Technologie",
        etat="Disponible",
        disponible=True,
        proprietaire=YASSINE,
        batiment="Bâtiment B · Labo Image",
        duree="Jusqu'à 4 jours",
        note=4.6,
        description=(
            "Boîtier reflex 24,2 Mpx avec objectif 18-55 mm, ideal pour les "
            "projets photographiques et les sorties de terrain."
        ),
        conditions=(
            "Carte mémoire remise et vidée avant restitution",
        ),
        visuel="camera",
    ),
    Objet(
        titre="Lampe de bureau LED réglable",
        categorie="Laboratoire",
        etat="Disponible",
        disponible=True,
        proprietaire=LINA,
        batiment="Bâtiment A · Salle 118",
        duree="Jusqu'à 10 jours",
        note=4.4,
        description="Lampe de bureau à intensité variable, parfaite pour les travaux de nuit.",
        conditions=("Restitution avant la fin du semestre",),
        visuel="lampe",
    ),
)


# ---------------------------------------------------------------------------
# Filieres proposees a l'inscription
# ---------------------------------------------------------------------------

FILIERES = (
    "Informatique",
    "Génie civil",
    "Mathématiques",
    "Biologie",
    "Physique",
    "Économie",
    "Droit",
)

NIVEAUX = ("L1", "L2", "L3", "Master 1", "Master 2", "Doctorat")


# ---------------------------------------------------------------------------
# Filieres/niveaux proposes dans le formulaire de demande
# ---------------------------------------------------------------------------

DUREES = ("24 heures", "2 jours", "3 jours", "1 semaine", "2 semaines")


def par_categorie(categorie: str) -> list[Objet]:
    return [o for o in OBJETS if o.categorie == categorie]


def trouver(titre: str) -> Objet:
    for objet in OBJETS:
        if objet.titre == titre:
            return objet
    raise KeyError(titre)
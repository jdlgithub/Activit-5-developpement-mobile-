"""Validation du document .epgz produit.

Usage :
    python3 -m src.valider [chemin.epgz]

Controles effectues :
  1. le conteneur est bien une archive TAR compressee en GZIP ;
  2. ``content.xml`` est present et declares chaque page une seule fois ;
  3. chaque page declaree existe dans l'archive ;
  4. tout le XML est bien forme et utilise le namespace Pencil attendu ;
  5. chaque forme porte les attributs obligatoires de Pencil
     (``id``, ``p:type``, ``p:def``, ``transform``) et un ``p:metadata`` ;
  6. toutes les proprietes ecrites sont reellement declarees par la forme
     dans le fichier de definition Pencil correspondant.

Le point 6 est le plus utile : il detecte toute propriete mal orthographiee,
qui serait silencieusement ignoree par Pencil.

Si les definitions natives de Pencil sont disponibles (variable
d'environnement ``PENCIL_STENCILS`` ou dossier ``reference/pencil`` versionne
avec le projet), le controle croise est actif ; sinon il est signale et
ignores. Les definitions sont versionnees pour que la validation soit
reproductible sans acces reseau ni a l'application Pencil installee.
"""

from __future__ import annotations

import os
import sys
import tarfile
import xml.etree.ElementTree as ET

from .pencil_writer import COLLECTION, NS_P, NS_SVG
from .build import NOM_DOCUMENT

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Proprietes communes a toutes les formes natives, ajoutees par le moteur.
PROPRIETES_MOTEUR = {"box"}

# Fichiers de definition de formes, cherches dans cet ordre.
# Les sources Pencil sont versionnees dans reference/pencil : le controle
# croise reste donc disponible meme sans application Pencil installee.
CANDIDATS_STENCILS = (
    os.environ.get("PENCIL_STENCILS", ""),
    os.path.join(RACINE, "reference", "pencil"),
    os.path.join(RACINE, "stencils"),
    "/tmp/opencode/pencil-src/app/stencils",
)


class Rapport:
    def __init__(self) -> None:
        self.erreurs: list[str] = []
        self.avertissements: list[str] = []
        self.infos: list[str] = []

    def erreur(self, message: str) -> None:
        self.erreurs.append(message)

    def avertissement(self, message: str) -> None:
        self.avertissements.append(message)

    def info(self, message: str) -> None:
        self.infos.append(message)

    @property
    def ok(self) -> bool:
        return not self.erreurs


def _p(tag: str) -> str:
    return "{%s}%s" % (NS_P, tag)


def _svg(tag: str) -> str:
    return "{%s}%s" % (NS_SVG, tag)


def charger_definitions() -> dict[str, set[str]] | None:
    """Charge les proprietes declarees par chaque forme des collections natives."""
    for racine in CANDIDATS_STENCILS:
        if not racine or not os.path.isdir(racine):
            continue
        commun = os.path.join(racine, "Common", "Definition.xml")
        if not os.path.isfile(commun):
            continue
        return _parser_definitions(commun, "Evolus.Common")
    return None


def _parser_definitions(chemin: str, prefixe_collection: str) -> dict[str, set[str]]:
    """Extrait, pour chaque forme, l'ensemble des noms de proprietes declares."""
    arbre = ET.parse(chemin)
    definitions: dict[str, set[str]] = {}
    for forme in arbre.getroot().iter(_p("Shape")):
        ident = forme.get("id")
        if not ident:
            continue
        proprietes: set[str] = set()
        for noeud in forme.iter():
            nom = noeud.get("name")
            if nom:
                proprietes.add(nom)
        definitions["%s:%s" % (prefixe_collection, ident)] = proprietes
    return definitions


def valider(chemin: str) -> Rapport:
    rapport = Rapport()

    # --- 1. Conteneur -------------------------------------------------------
    if not tarfile.is_tarfile(chemin):
        rapport.erreur("Le fichier n'est pas une archive TAR valide.")
        return rapport
    try:
        with gzip_open(chemin) as brut:
            entree = tarfile.open(fileobj=brut, mode="r:")
            membres = entree.getnames()
            if "content.xml" not in membres:
                rapport.erreur("content.xml est absent de l'archive.")
                return rapport
            pages = {
                nom: entree.extractfile(nom).read().decode("utf-8")
                for nom in membres
                if nom.endswith(".xml")
            }
    except OSError as exc:
        rapport.erreur("Archive illisible : %s" % exc)
        return rapport

    rapport.info("Archive TAR/GZIP valide — %d entrées, %d fichiers XML" % (len(membres), len(pages)))

    # --- 2/3. content.xml et coherence des pages -----------------------------
    try:
        contenu = ET.fromstring(pages["content.xml"])
    except ET.ParseError as exc:
        rapport.erreur("content.xml mal formé : %s" % exc)
        return rapport

    if contenu.tag != _p("Document"):
        rapport.erreur("Racine de content.xml inattendue : %s (attendu %s)" % (contenu.tag, _p("Document")))

    noeuds_page = list(contenu.iter(_p("Page")))
    if not noeuds_page:
        rapport.erreur("content.xml ne declare aucune page.")
        return rapport
    rapport.info("content.xml declare %d pages" % len(noeuds_page))

    vues: set[str] = set()
    total_formes = 0
    total_textes = 0

    definitions = charger_definitions()
    if definitions is None:
        rapport.avertissement(
            "Définitions natives de Pencil introuvables : le contrôle croisé "
            "des propriétés est ignoré (définir PENCIL_STENCILS pour l'activer)."
        )

    # --- 4/5/6. Pages et formes ---------------------------------------------
    for index, noeud in enumerate(noeuds_page, start=1):
        href = noeud.get("href")
        if not href:
            rapport.erreur("Page %d : attribut href manquant." % index)
            continue
        if href in vues:
            rapport.erreur("Page %d : href dupliqué (%s)." % (index, href))
        vues.add(href)
        if href not in pages:
            rapport.erreur("Page %d : le fichier %s est absent de l'archive." % (index, href))
            continue

        try:
            page = ET.fromstring(pages[href])
        except ET.ParseError as exc:
            rapport.erreur("Page %s : XML mal formé (%s)." % (href, exc))
            continue

        _valider_page(page, href, index, definitions, rapport)
        total_formes += len(list(page.iter(_svg("g"))))
        total_textes += len(list(page.iter(_p("property"))))

    rapport.info("%d formes et %d propriétés au total" % (total_formes, total_textes))
    return rapport


def _valider_page(
    page: ET.Element,
    href: str,
    index: int,
    definitions: dict[str, set[str]] | None,
    rapport: Rapport,
) -> None:
    if page.tag != _p("Page"):
        rapport.erreur("Page %s : racine inattendue %s." % (href, page.tag))
        return

    # Proprietes de page.
    proprietes = {
        noeud.get("name"): (noeud.text or "")
        for noeud in page.iter(_p("Property"))
    }
    for obligatoire in ("id", "name", "width", "height"):
        if obligatoire not in proprietes:
            rapport.erreur("Page %s : propriété obligatoire absente (%s)." % (href, obligatoire))
    try:
        int(float(proprietes.get("width", "0")))
        int(float(proprietes.get("height", "0")))
    except ValueError:
        rapport.erreur("Page %s : width/height non numeriques." % href)

    contenu = page.find(_p("Content"))
    if contenu is None:
        rapport.erreur("Page %s : élément p:Content absent." % href)
        return

    formes = [g for g in contenu.iter(_svg("g")) if g.get(_p("type")) == "Shape"]
    if not formes:
        rapport.avertissement("Page %s : aucune forme." % href)

    deja_signale: set[str] = set()

    def _signaler_unique(cle: str, message: str) -> None:
        """Ne signale qu'une fois par page et par cle."""
        if cle in deja_signale:
            return
        deja_signale.add(cle)
        rapport.erreur(message)

    for forme in formes:
        ident = forme.get("id")
        definition = forme.get(_p("def"))
        transform = forme.get("transform")
        meta = forme.find(_p("metadata"))

        if not ident:
            rapport.erreur("Page %s : forme sans identifiant." % href)
        if not definition:
            rapport.erreur("Page %s : forme %s sans p:def." % (href, ident))
            continue
        if not transform:
            rapport.erreur("Page %s : forme %s sans transform." % (href, ident))
        elif not transform.startswith("translate("):
            rapport.erreur(
                "Page %s : forme %s, transform inattendu (%s)." % (href, ident, transform)
            )
        if meta is None:
            rapport.erreur("Page %s : forme %s sans p:metadata." % (href, ident))
            continue

        collection, _, forme_id = definition.partition(":")
        if collection != COLLECTION:
            rapport.avertissement(
                "Page %s : forme %s referencing une collection inconnue (%s)." % (href, ident, definition)
            )
            continue

        connues = definitions.get(definition) if definitions else None
        if definitions is not None and connues is None:
            _signaler_unique(
                "forme:" + definition,
                "Page %s : la forme %s n'existe pas dans %s." % (href, forme_id, COLLECTION),
            )
            continue

        proprietes_connues = set(connues or ()) | PROPRIETES_MOTEUR
        # Sans les definitions natives, on ne peut rien affirmer sur les
        # proprietes : le controle croise est ignore plutot que de tout
        # signaler comme inconnu.
        definitions_disponibles = definitions is not None and connues is not None
        vues = set()
        for noeud in meta.findall(_p("property")):
            nom = noeud.get("name")
            if not nom:
                rapport.erreur("Page %s : p:property sans attribut name." % href)
                continue
            if nom in vues:
                _signaler_unique(
                    "double:" + nom,
                    "Page %s : propriété %s dupliquée." % (href, nom),
                )
            vues.add(nom)
            if definitions_disponibles and nom not in proprietes_connues:
                _signaler_unique(
                    "prop:%s:%s" % (forme_id, nom),
                    "Page %s : propriété « %s » inconnue pour la forme %s." % (href, nom, forme_id),
                )


def gzip_open(chemin: str):
    import gzip

    return gzip.open(chemin, "rb")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    chemin = args[0] if args else os.path.join(RACINE, "out", NOM_DOCUMENT)

    if not os.path.isfile(chemin):
        print("Fichier introuvable : %s" % chemin)
        return 2

    rapport = valider(chemin)
    print("Validation de %s" % chemin)
    for ligne in rapport.infos:
        print("  [info] %s" % ligne)
    for ligne in rapport.avertissements:
        print("  [avertissement] %s" % ligne)
    for ligne in rapport.erreurs:
        print("  [ERREUR] %s" % ligne)

    if rapport.ok:
        print("=> Document Pencil valide.")
        return 0
    print("=> %d erreur(s) a corriger." % len(rapport.erreurs))
    return 1


if __name__ == "__main__":
    sys.exit(main())
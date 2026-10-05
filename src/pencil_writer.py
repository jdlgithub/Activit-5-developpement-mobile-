"""Generateur de documents Pencil (format .epgz).

Produit un fichier .epgz lisible par Pencil (Evolus Pencil v3.x).

Structure du conteneur
----------------------
Un .epgz est une archive TAR compressee en GZIP (et non un ZIP) contenant :

    content.xml          index du document : proprietes + liste des pages
    page_<id>.xml        un fichier par page (une maquette)
    fonts/               facultatif, polices embarquees

Format des pages (identique a la sortie de Pencil) :

    <p:Page>
      <p:Properties>
        <p:Property name="name">...</p:Property>
      </p:Properties>
      <p:Content>
        <svg:g p:type="Shape" p:def="Evolus.Common:RoundedRect"
               id="..." transform="translate(x,y)">
          <p:metadata>
            <p:property name="box"><![CDATA[320,48]]></p:property>
          </p:metadata>
        </svg:g>
      </p:Content>
    </p:Page>

Pencil regenere le rendu visuel de chaque forme a partir de sa definition
(p:def) : seules les proprietes en <p:metadata> doivent etre fournies.
"""

from __future__ import annotations

import io
import tarfile
import uuid
from typing import Iterable
from xml.sax.saxutils import escape, quoteattr

from . import charte
from .scene import Ecran, Ellipse, Forme, FormeTexte, Image, Ligne, Texte

# ---------------------------------------------------------------------------
# Espaces de noms
# ---------------------------------------------------------------------------

NS_P = "http://www.evolus.vn/Namespace/Pencil"
NS_SVG = "http://www.w3.org/2000/svg"
NS_XLINK = "http://www.w3.org/1999/xlink"

DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>\n'

# Collection de formes natives livree avec Pencil.
COLLECTION = "Evolus.Common"

# Correspondance entre les primitives de la scene et les formes Pencil.
FORME_RECT = COLLECTION + ":RoundedRect"
FORME_TEXTE = COLLECTION + ":RichTextBoxV2"
FORME_LIGNE = COLLECTION + ":Line"
FORME_ELLIPSE = COLLECTION + ":ms-oval"
FORME_IMAGE = COLLECTION + ":Bitmap"


class _Uid:
    """Generateur d'identifiants stables et uniques."""

    def __init__(self, prefixe: str = "") -> None:
        self._prefixe = prefixe
        self._compteur = 0

    def __call__(self) -> str:
        self._compteur += 1
        alea = uuid.uuid4().hex[:8]
        return "%s%04d%s" % (self._prefixe, self._compteur, alea)


def _brut(valeur) -> str:
    """Normalise une valeur de propriete Pencil (None -> chaine vide)."""
    if valeur is None:
        return ""
    return str(valeur)


def _couleur(valeur, defaut: str) -> str:
    """Normalise une couleur vers le format Pencil #RRGGBBAA."""
    if not valeur:
        return defaut
    couleur = str(valeur).strip()
    if not couleur:
        return defaut
    if couleur.startswith("#") and len(couleur) == 7:
        return couleur.upper() + "FF"
    if couleur.startswith("#") and len(couleur) == 9:
        return couleur.upper()
    if couleur.startswith("rgba(") or couleur.startswith("rgb("):
        return couleur
    return defaut


def _metadata(forme) -> list[tuple[str, str]]:
    """Proprietes effectivement pertinentes pour chaque type de forme."""
    if isinstance(forme, FormeTexte):
        brut = forme.properties()
        return [
            ("box", brut["box"]),
            ("fillColor", _couleur(brut["fillColor"], "#FFFFFF00")),
            ("strokeColor", _couleur(brut["strokeColor"], "#000000FF")),
            ("strokeStyle", brut["strokeStyle"]),
            ("radius", brut["radius"]),
            ("withBlur", "false"),
            ("textContent", brut["textContent"]),
            ("textFont", brut["textFont"]),
            ("textColor", _couleur(brut["textColor"], "#000000FF")),
            ("textAlign", brut["textAlign"]),
            ("textPadding", brut["textPadding"]),
        ]

    if isinstance(forme, Forme):
        brut = forme.properties()
        return [
            ("box", brut["box"]),
            ("fillColor", _couleur(brut["fillColor"], "#FFFFFF00")),
            ("strokeColor", _couleur(brut["strokeColor"], "#000000FF")),
            ("strokeStyle", brut["strokeStyle"]),
            ("radius", brut["radius"]),
            ("withBlur", "false"),
            ("textPadding", "0,10"),
        ]

    if isinstance(forme, Texte):
        brut = forme.properties()
        return [
            ("fixedWidth", "true"),
            ("width", brut["width"]),
            ("textContent", brut["textContent"]),
            ("textFont", brut["textFont"]),
            ("textColor", _couleur(brut["textColor"], "#000000FF")),
            ("customStyle", brut["customStyle"]),
        ]

    if isinstance(forme, Ellipse):
        brut = forme.properties()
        return [
            ("box", brut["box"]),
            ("fillColor", _couleur(brut["fillColor"], "#FFFFFF00")),
            ("strokeColor", _couleur(brut["strokeColor"], "#000000FF")),
            ("strokeStyle", brut["strokeStyle"]),
            ("textPadding", "0,0"),
        ]

    if isinstance(forme, Ligne):
        return [
            ("box", "%g,%g" % (max(0.0, forme.x2 - forme.x1), max(1.0, forme.y2 - forme.y1))),
            ("strokeColor", _couleur(forme.couleur, "#000000FF")),
            ("strokeStyle", "%g|%s" % (max(1, round(forme.epaisseur)), "solid")),
        ]

    if isinstance(forme, Image):
        brut = forme.properties()
        # Format ImageData de Pencil : "<largeur>,<hauteur>,<data-uri>"
        return [
            ("box", brut["box"]),
            ("imageData", "%g,%g,%s" % (forme.l, forme.h, forme.donnees)),
            ("fillColor", "#FFFFFF00"),
            ("strokeColor", "#000000FF"),
            ("strokeStyle", "0|"),
            ("withBlur", "false"),
        ]

    raise TypeError("Primitive non supportee : %r" % type(forme).__name__)


def _position(forme) -> tuple[float, float]:
    """Position de la forme, portee par l'attribut SVG transform."""
    if isinstance(forme, Ligne):
        return forme.x1, forme.y1
    return forme.x, forme.y


def _definition(forme) -> str:
    if isinstance(forme, (Forme, FormeTexte)):
        return FORME_RECT
    if isinstance(forme, Texte):
        return FORME_TEXTE
    if isinstance(forme, Ligne):
        return FORME_LIGNE
    if isinstance(forme, Ellipse):
        return FORME_ELLIPSE
    if isinstance(forme, Image):
        return FORME_IMAGE
    raise TypeError("Primitive non supportee : %r" % type(forme).__name__)


class PencilDocumentWriter:
    """Construit un document Pencil a partir d'une liste d'ecrans."""

    def __init__(self, nom_document: str = "CampusShare") -> None:
        self.nom_document = nom_document
        self.ecrans: list[Ecran] = []
        self.uid = _Uid()
        # identifiant de page interne, associe au nom d'ecran
        self._ids: dict[str, str] = {}

    # -- API -----------------------------------------------------------------

    def ajouter_ecran(self, ecran: Ecran) -> None:
        self.ecrans.append(ecran)

    def ecrire(self, chemin: str) -> str:
        """Ecrit le .epgz et retourne le chemin ecrit."""
        pages: list[tuple[Ecran, str]] = []
        for ecran in self.ecrans:
            nom_fichier = self._nom_fichier_page(ecran)
            pages.append((ecran, nom_fichier))

        contenu_xml = self._content_xml(pages).encode("utf-8")
        pages_xml = [(nom, self._page_xml(ecran).encode("utf-8")) for ecran, nom in pages]

        # tarfile gere lui-meme la compression gzip du .epgz.
        with open(chemin, "wb") as sortie:
            with tarfile.open(fileobj=sortie, mode="w:gz") as archive:
                self._ajouter(archive, "content.xml", contenu_xml)
                for nom_fichier, contenu in pages_xml:
                    self._ajouter(archive, nom_fichier, contenu)
        return chemin

    # -- Interne -------------------------------------------------------------

    @staticmethod
    def _ajouter(archive: tarfile.TarFile, nom: str, donnees: bytes) -> None:
        info = tarfile.TarInfo(name=nom)
        info.size = len(donnees)
        info.mtime = 0
        info.mode = 0o644
        archive.addfile(info, io.BytesIO(donnees))

    def _nom_fichier_page(self, ecran: Ecran) -> str:
        """Nom de fichier interne de la page (identique au modele Pencil)."""
        ident = uuid.uuid4().hex
        self._ids[ecran.nom] = ident
        return "page_%s.xml" % ident

    def _content_xml(self, pages: Iterable[tuple[Ecran, str]]) -> str:
        morceaux = [
            DECLARATION,
            '<Document xmlns=%s>' % quoteattr(NS_P),
            "  <Properties>",
            "    <Property name=%s>%s</Property>" % (quoteattr("name"), escape(self.nom_document)),
            "    <Property name=%s>%s</Property>" % (quoteattr("fileVersion"), escape("3.0.0")),
            "    <Property name=%s>%s</Property>" % (quoteattr("creator"), escape("CampusShare / OpenCode")),
            "  </Properties>",
            "  <Pages>",
        ]
        for _, nom_fichier in pages:
            morceaux.append('    <Page href=%s/>' % quoteattr(nom_fichier))
        morceaux += ["  </Pages>", "</Document>", ""]
        return "\n".join(morceaux)

    def _page_xml(self, ecran: Ecran) -> str:
        ident = self._ids[ecran.nom]
        proprietes = [
            ("id", ident),
            ("fid", ident),
            ("name", ecran.nom),
            ("width", str(ecran.largeur)),
            ("height", str(ecran.hauteur)),
            ("backgroundColor", charte.avec_alpha(ecran.fond)),
            ("note", _note_xml(ecran.note)),
            ("pageFileName", "page_%s.xml" % ident),
            ("scrollTop", "0"),
            ("scrollLeft", "0"),
            ("zoom", "1"),
        ]
        morceaux = [
            DECLARATION,
            "<p:Page xmlns:p=%s xmlns:svg=%s xmlns:xlink=%s>" % (quoteattr(NS_P), quoteattr(NS_SVG), quoteattr(NS_XLINK)),
            "  <p:Properties>",
        ]
        for nom, valeur in proprietes:
            morceaux.append(
                "    <p:Property name=%s>%s</p:Property>" % (quoteattr(nom), escape(_brut(valeur)))
            )
        morceaux += ["  </p:Properties>", "  <p:Content>"]

        for forme in ecran.formes:
            morceaux.append(_forme_xml(forme, self.uid))

        morceaux += ["  </p:Content>", "</p:Page>", ""]
        return "\n".join(morceaux)


def _note_xml(note: str) -> str:
    """Les notes de page sont du texte riche : on echappe le HTML."""
    return escape(note)


def _forme_xml(forme, uid: _Uid, indent: str = "    ") -> str:
    """Serialise une primitive en noeud de forme Pencil."""
    definition = _definition(forme)
    x, y = _position(forme)
    ident = uid()
    nom = forme.nom

    attributs = [
        ("id", ident),
        ("p:type", "Shape"),
        ("p:def", definition),
        ("transform", "translate(%g,%g)" % (x, y)),
    ]
    if nom:
        attributs.append(("p:name", nom))
    attr_xml = " ".join("%s=%s" % (cle, quoteattr(valeur)) for cle, valeur in attributs)

    lignes = ["%s<svg:g %s>" % (indent, attr_xml), "%s  <p:metadata>" % indent]
    for nom_prop, valeur in _metadata(forme):
        if valeur == "":
            continue
        # CDATA : preserve la mise en forme exacte du texte et evite tout
        # conflit avec le caractere & dans le HTML du texte riche.
        lignes.append(
            "%s    <p:property name=%s><![CDATA[%s]]></p:property>"
            % (indent, quoteattr(nom_prop), _cdata(valeur))
        )
    lignes += ["%s  </p:metadata>" % indent, "%s</svg:g>" % indent]
    return "\n".join(lignes)


def _cdata(valeur: str) -> str:
    """Protege la sequence fermante CDATA eventuellement presente."""
    return valeur.replace("]]>", "]]]]><![CDATA[>")
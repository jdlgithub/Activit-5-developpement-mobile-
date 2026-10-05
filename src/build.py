"""Assemblage de tous les ecrans et production des livrables.

Usage :
    python3 -m src.build

Produit :
    out/CampusShare_Maquettes.epgz   document Pencil (8 ecrans)
    out/apercu/*.svg                 un SVG par ecran
    out/apercu/planche.html          planche de contact
    out/apercu/*.png                 apercus rasterises (si Chrome est present)
    out/rapport_generation.txt       synthese de la generation

Options :
    --sans-png     ne pas rasteriser les SVG (build rapide, ~1 s)
    --jobs=N       instances Chrome simultanees pour la rasterisation (4)
"""

from __future__ import annotations

import concurrent.futures
import os
import shutil
import subprocess
import sys
import tempfile

from . import ecrans as dossier_ecrans
from .pencil_writer import PencilDocumentWriter
from .rendu_svg import rendre_ecran, rendre_gallery
from .scene import Ecran

# ---------------------------------------------------------------------------
# Sorties
# ---------------------------------------------------------------------------

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_OUT = os.path.join(RACINE, "out")
DOSSIER_APERCU = os.path.join(DOSSIER_OUT, "apercu")
NOM_DOCUMENT = "CampusShare_Maquettes.epgz"
NOM_RAPPORT = "rapport_generation.txt"

# Modules d'ecrans, dans l'ordre de navigation de l'application.
MODULES_ECRANS = (
    "ecran01_accueil",
    "ecran02_connexion",
    "ecran03_inscription",
    "ecran04_tableau_bord",
    "ecran05_detail_objet",
    "ecran06_demande_pret",
    "ecran07_publication",
    "ecran08_profil",
)


def charger_ecrans() -> list[Ecran]:
    """Instancie chaque ecran dans l'ordre du parcours utilisateur."""
    ecrans = []
    for nom_module in MODULES_ECRANS:
        module = getattr(dossier_ecrans, nom_module)
        ecran = module.construire()
        ecrans.append(ecran)
    return ecrans


def ecrire_pencil(ecrans: list[Ecran], chemin: str) -> int:
    """Ecrit le document Pencil et retourne le nombre de formes."""
    redacteur = PencilDocumentWriter(nom_document="CampusShare — maquettes mobiles")
    for ecran in ecrans:
        redacteur.ajouter_ecran(ecran)
    redacteur.ecrire(chemin)
    return sum(e.nombre_formes for e in ecrans)


def ecrire_apercus(ecrans: list[Ecran], dossier: str) -> list[str]:
    """Ecrit un SVG par ecran et la planche de contact."""
    os.makedirs(dossier, exist_ok=True)
    chemins = []
    for index, ecran in enumerate(ecrans, start=1):
        chemin = os.path.join(dossier, "%02d_%s.svg" % (index, _slug(ecran.nom)))
        with open(chemin, "w", encoding="utf-8") as sortie:
            sortie.write(rendre_ecran(ecran))
        chemins.append(chemin)

    with open(os.path.join(dossier, "planche.html"), "w", encoding="utf-8") as sortie:
        sortie.write(rendre_gallery(ecrans, colonnes=4))
    return chemins


def rasteriser(chemins: list[str], dossier: str, jobs: int = 4) -> int:
    """Rasterise les SVG en PNG via Chrome headless.

    Deux precautions indispensables :

      - chaque instance reçoit son propre ``--user-data-dir``, sans quoi Chrome
        applique un verrou de singleton et les lancements paralleles se
        bloqueent indefiniment ;
      - le nombre d'instances simultanees est borne (Chrome est gourmand) ;
      - l'attente est un delai global : une instance bloquee ne retarde pas les
        autres, et les PNG deja ecrits ne sont pas regeneres.
    """
    navigateur = _trouver_chrome()
    if not navigateur:
        return 0

    restants = []
    for chemin in chemins:
        png = os.path.splitext(chemin)[0] + ".png"
        if not (os.path.exists(png) and os.path.getsize(png) > 0):
            restants.append((chemin, png))

    produits = 0
    if restants:
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executeur:
            resultats = executeur.map(
                lambda cible: _rasteriser_une(navigateur, *cible), restants
            )
            produits = sum(1 for r in resultats if r)
    return produits + (len(chemins) - len(restants))


def _rasteriser_une(navigateur: str, chemin: str, png: str) -> bool:
    """Lance Chrome sur un SVG et retourne True si le PNG a bien ete produit."""
    if os.path.exists(png):
        os.remove(png)
    with tempfile.TemporaryDirectory(prefix="campuschrome-") as profil:
        commande = [
            navigateur,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--hide-scrollbars",
            "--user-data-dir=%s" % profil,
            "--force-device-scale-factor=2",
            "--screenshot=%s" % png,
            "--window-size=360,800",
            "file://%s" % os.path.abspath(chemin),
        ]
        try:
            subprocess.run(
                commande,
                check=True,
                timeout=120,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            return False
    return os.path.exists(png) and os.path.getsize(png) > 0


def _slug(nom: str) -> str:
    caracteres = [c if c.isalnum() else "_" for c in nom.lower()]
    return "".join(caracteres).strip("_").replace("__", "_")


def _trouver_chrome() -> str | None:
    for nom in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    return None


def ecrire_rapport(ecrans: list[Ecran], chemin: str, nb_formes: int, nb_svg: int,
                   nb_png: int | None) -> None:
    """Ecrit la synthese de generation annoncee dans la docstring du module."""
    from datetime import datetime

    from . import charte

    lignes = [
        "CampusShare — synthese de generation des maquettes",
        "=" * 52,
        "",
        "Date            : %s" % datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Document Pencil : out/%s" % NOM_DOCUMENT,
        "Format          : 8 pages, %d x %d px, portrait" % (charte.LARGEUR_ECRAN, charte.HAUTEUR_ECRAN),
        "",
        "Formes totales  : %d" % nb_formes,
        "Apercus SVG     : %d" % nb_svg,
        "Apercus PNG     : %s" % (nb_png if nb_png is not None else "non demandes (--sans-png)"),
        "",
        "Charte",
        "-" * 52,
        "Vert principal : %s" % charte.VERT,
        "Orange accent   : %s" % charte.ORANGE,
        "Fond / surface  : %s / %s" % (charte.FOND, charte.SURFACE),
        "Police          : %s" % charte.POLICE,
        "Cible tactile   : %d px minimum" % charte.CIBLE_MIN,
        "",
        "Ecrans",
        "-" * 52,
    ]
    for index, ecran in enumerate(ecrans, start=1):
        # Le nom de l'ecran porte deja son numero ("04 · ..."), on ne le repete pas.
        libelle = ecran.nom.split("·", 1)[-1].strip()
        lignes.append("%02d. %-34s %4d formes" % (index, libelle, ecran.nombre_formes))
    lignes += [
        "",
        "Verification",
        "-" * 52,
        "python3 -m src.valider  structure du .epgz et proprietes natives",
        "python3 -m src.linter   debordements, collisions, cibles tactiles, charte",
        "",
    ]
    with open(chemin, "w", encoding="utf-8") as sortie:
        sortie.write("\n".join(lignes))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    connus = {"--sans-png", "--jobs"}
    inconnus = [a for a in args if a not in connus and not a.startswith("--jobs=")]
    if inconnus:
        print("Option inconnue : %s" % ", ".join(inconnus))
        print("Options disponibles : --sans-png, --jobs=N")
        return 2
    with_png = "--sans-png" not in args
    jobs = 4
    for arg in args:
        if arg.startswith("--jobs="):
            jobs = max(1, int(arg.split("=", 1)[1]))

    ecrans = charger_ecrans()

    os.makedirs(DOSSIER_OUT, exist_ok=True)
    chemin_pencil = os.path.join(DOSSIER_OUT, NOM_DOCUMENT)
    nb_formes = ecrire_pencil(ecrans, chemin_pencil)
    print("Pencil   : %s (%d formes)" % (chemin_pencil, nb_formes))

    chemins = ecrire_apercus(ecrans, DOSSIER_APERCU)
    print("Apercus  : %d SVG + planche.html" % len(chemins))

    nb_png = None
    if with_png:
        nb_png = rasteriser(chemins, DOSSIER_APERCU, jobs=jobs)
        if nb_png:
            print("PNG      : %d apercus rasterises" % nb_png)
        else:
            print("PNG      : ignore (navigateur headless introuvable)")

    chemin_rapport = os.path.join(DOSSIER_OUT, NOM_RAPPORT)
    ecrire_rapport(ecrans, chemin_rapport, nb_formes, len(chemins), nb_png)
    print("Rapport  : %s" % chemin_rapport)

    for ecran in ecrans:
        print("  - %-28s %4d formes" % (ecran.nom, ecran.nombre_formes))

    return 0


if __name__ == "__main__":
    sys.exit(main())
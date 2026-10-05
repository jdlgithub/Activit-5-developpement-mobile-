# CampusShare — utiliser les maquettes dans Pencil et les présenter

Ce document accompagne le fichier `out/CampusShare_Maquettes.epgz`.
Il explique comment ouvrir les maquettes, comment les modifier, et comment
les présenter à un jury ou une équipe.

---

## 1. Le document en bref

| | |
|---|---|
| Fichier | `out/CampusShare_Maquettes.epgz` |
| Format | archive **TAR compressée GZIP** (ce n'est pas un ZIP) |
| Contenu | 8 pages, 579 formes, 2645 propriétés |
| Format de chaque page | **360 × 800 px**, mobile portrait |
| Taille d'un écran auiversal | 18 Ko pour les 8 pages |

Pour ouvrir le fichier dans un explorateur d'archives, utilisez
`file-roller`, `Archive Manager` ou `tar -tzf` en ligne de commande.
L'archive contient :

```
content.xml              description du document et liste des pages
page_<id>.xml            une page par maquette
```

`content.xml` est l'entrée à lire en premier : il donne l'ordre des pages
et leur nom. Les identifiants de page sont des chaînes hexadécimales, pas
des numéros : c'est le nom porté par `content.xml` qui fait foi.

---

## 2. Ouvrir dans Pencil

1. Lancez **Pencil**.
2. `Open` → sélectionnez `out/CampusShare_Maquettes.epgz`.
3. La liste des pages apparaît dans le panneau de gauche, dans l'ordre du
   parcours utilisateur.

### Si Pencil ne s'ouvre pas

Le binaire Pencil 3 officiel ne démarre pas sous Ubuntu 26.04 : il exige
`libgtk-x11-2.0`, `libgdk-x11-2.0` et `libgconf-2`, qui ne sont plus
fournis par les dépôts actuels, et il n'existe pas de version Linux plus
récente.

Le document a donc été produit et vérifié **sans passer par l'application** :

- le format a été relevé sur les sources `evolus/pencil` et sur
  l'archive officielle ;
- chaque propriété générée est recoupée avec les définitions natives des
  formes, versionnées dans `reference/pencil/Common/Definition.xml` ;
- les formes utilisées sont limited à quatre formes natives stables :
  `RoundedRect`, `RichTextBoxV2`, `Line` et `ms-oval`.

Pour ouvrir le document malgré tout, dans un environnement compatible :

```bash
# machine sous Ubuntu 20.04 ou Debian 11, par exemple
sudo apt install libgtk2.0-0 libgconf-2-4
```

ou dans une machine virtuelle, un conteneur, ou une autre distribution.

---

## 3. Modifier les maquettes

**Le document Pencil n'est pas la source.** Les maquettes sont décrites dans
le code Python de `src/`, et le `.epgz` est régénéré. Modifier le `.epgz` à
la main est possible pour une retouche ponctuelle, mais la modification sera
perdue au prochain build.

### Régénérer

```bash
python3 -m src.build              # tout, y compris les PNG (~70 s)
python3 -m src.build --sans-png   # document et SVG seulement (~1 s)
python3 -m src.build --jobs=2     # limite les instances Chrome
```

Sorties :

| Fichier | Rôle |
|---|---|
| `out/CampusShare_Maquettes.epgz` | document Pencil |
| `out/apercu/NN_....svg` | un SVG par écran |
| `out/apercu/NN_....png` | aperçu rasterisé, 720 × 1600 |
| `out/apercu/planche.html` | planche de contact, les 8 écrans côte à côte |
| `out/rapport_generation.txt` | synthèse de génération |

### Vérifier avant de présenter

```bash
python3 -m src.valider   # structure du .epgz et propriétés natives
python3 -m src.linter    # débordements, collisions, cibles tactiles, charte
```

Les deux commandes doivent finir par `valide` et `0 erreur(s)`.
Ne présentez pas un document qui n'est pas validé.

### Où changer quoi

| Pour changer | Modifiez |
|---|---|
| une couleur, une taille de police, une marge | `src/charte.py` |
| un bouton, une carte, une icône, une barre | `src/composants.py` |
| le texte d'un exemple (objets, étudiants) | `src/donnees.py` |
| la mise en page d'un écran | `src/ecrans/ecranNN_*.py` |
| l'ordre des pages | `MODULES_ECRANS` dans `src/build.py` |

Tout changement de couleur ou de police se répercute automatiquement sur
les huit écrans : c'est l'intérêt de la charte centralisée.

---

## 4. Conventions à respecter

Ces règles sont appliquées automatiquement par `src/linter.py`. Les
respecter évite de devoir corriger après coup.

- **Cible tactile** : 44 px minimum pour un bouton. Les pastilles d'état
  font 22 px, les puces de filtre 32 px — ce ne sont pas des boutons.
- **Rien hors cadre** : aucun élément au-delà de x=360 ou y=800. Une rangée
  de puces trop large se tronque via `rangee_puces()` au lieu de déborder.
- **Barres fixes** : la barre d'onglets et la barre d'action sont dessinées
  en dernier, et aucun contenu ne passe dessous.
- **Une seule famille typographique**, un seul niveau d'elevation, deux
  couleurs porteuses : le vert et l'orange.
- **Palette fermée** : toute couleur hors charte est signalée.

---

## 5. Présenter les maquettes

### Ordre de présentation

Le parcours suit la logique du produit, pas l'ordre des fichiers :

| | Écran | Le point à défendre |
|---|---|---|
| 1 | **Accueil / Bienvenue** | La promesse et l'accès direct à la connexion |
| 2 | **Connexion** | Le champ « email institutionnel » ancre le produit au campus |
| 3 | **Inscription** | La validation montre qu'on a pensé au cas réel |
| 4 | **Tableau de bord** | La valeur : on voit ce qui est disponible autour de soi |
| 5 | **Détail de l'objet** | La confiance : notations, propriétaire, état |
| 6 | **Demande de prêt** | La transformation d'un objet en échange |
| 7 | **Publication** | Le modèle participatif : le campus est le stock |
| 8 | **Profil & annonces** | La boucle est bouclée, l'emprunteur devient contributeur |

### Durée conseillée : 10 minutes

| | Durée | Contenu |
|---|---|---|
| Contexte | 1 min | Le campus jette, les étudiants rachètent. Pas d'achat, pas de vendeur. |
| Charte | 1 min | Deux couleurs, une police, 44 px de cible tactile. Montrer `charte.py`. |
| Parcours | 5 min | Les huit écrans, dans l'ordre ci-dessus. |
| Vérification | 2 min | `valider` et `linter`, pour montrer que le rendu est contrôlé. |
| Limites | 1 min | Voir ci-dessous. |

### Support

- **`out/apercu/planche.html`** : la vue d'ensemble. À ouvrir en premier,
  elle donne le rythme et sert d'accroche.
- **Les PNG** : à projeter un par un, en pleine page.
- **Le `.epgz`** : à ouvrir seulement si la question porte sur la
  vectorisation ou sur la reprise dans Pencil.

### Ce qu'il faut savoir dire si on pose des questions

- **« Pourquoi des formes d'image vides ? »** — les visuels d'objets sont
  des placeholders. Ce sont des zones réservées, pas des illustrations
  manquantes.
- **« Les textures de photo n'existent pas ? »** — volontairement : ce sont
  des maquettes d'interface, pas d'illustration. Le texte et les zones
  d'action sont complets.
- **« C'est validé comment ? »** — automatiquement, à chaque build, contre
  les définitions de formes de Pencil elles-mêmes.

### Limites à annoncer d'emblée

Ce sont les points faibles réels, il vaut mieux les nommer que les laisser
découvrir :

1. **Le parcours est linéaire.** Il n'y a pas d'écran « mes emprunts » ni
   de gestion de notification, alors que la cloche de l'écran 4 en suppose
   une. L'écran 8 couvre partiellement ce manque.
2. **Aucun état d'erreur.** Les champs sont vides et valides. Les variantes
   « email déjà utilisé », « objet indisponible entre-temps » ou « conflit
   de dates » n'ont pas été maquettées.
3. **Pas de version tablette ni web.** Le format est fixé à 360 × 800 px.
4. **La navigation entre écrans n'est pas câblée.** Pencil 3 ne propose pas
   de lien d'écran dans ce format : les transitions sont à prouver en
   prototype.

Ces quatre points sont la suite logique du travail, et c'est un bon terrain
pour une question de jury.

---

## 6. Commandes, en un coup d'œil

```bash
python3 -m src.build --sans-png   # régénérer le document et les SVG
python3 -m src.build              # + les PNG
python3 -m src.valider            # structure du .epgz, propriétés Pencil
python3 -m src.linter             # mise en page, cibles tactiles, charte
```

`--sans-png` pour itérer vite, sans `--sans-png` pour produire les supports
de présentation.
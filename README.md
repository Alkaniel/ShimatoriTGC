# 🌸 Shimatori TCG

> **"Là où le devoir rencontre le destin."**

**Shimatori TCG** est un jeu de cartes à collectionner (TCG) stratégique au tour par tour, développé en Python avec la bibliothèque **Pygame**. Plongez dans un univers inspiré du Japon féodal fantastique et prenez le contrôle du clan **Hoshikawa** ou de ses rivaux pour dominer le champ de bataille face à l'invasion Mongole.

---

## Sommaire
1. [Fonctionnalités](#-fonctionnalités)
2. [Installation & Lancement](#-installation--lancement)
3. [Comment Jouer](#-comment-jouer)
4. [Lore & Factions](#-lore--factions)
5. [Architecture Technique](#-architecture-technique)
6. [Crédits](#-crédits)

---

## Fonctionnalités

* **Système de Combat Complet :** Gestion des points de vie, attaque, mana et cimetière.
* **Unités & Rituels :** Invoquez des samouraïs puissants ou lancez des sorts dévastateurs (Dégâts directs, Buffs).
* **Mécaniques de Jeu Avancées :**
    * **Provocation (Taunt) :** Protège vos autres unités.
    * **Charge :** Attaque dès le tour où elle est jouée.
    * **Furtivité (Stealth) :** Inciblable tant qu'elle n'attaque pas.
    * **Bouclier Divin :** Ignore la première source de dégâts.
    * **Toxique :** Tue n'importe quelle unité touchée instantanément.
* **Interface Riche :**
    * Menu Collection avec vue détaillée et lore.
    * Zoom sur les cartes au survol (Hover).
    * Feedback visuel ("Juice") : Textes flottants de dégâts, soins et statuts.
* **Intelligence Artificielle :** Un adversaire capable de jouer des unités, lancer des sorts et choisir ses cibles.

---

## Installation & Lancement

### Prérequis
* Python 3.10 ou supérieur.
* Pip (Gestionnaire de paquets).

### 1. Cloner ou Télécharger le projet
```bash
git clone [https://github.com/votre-repo/shimatori-tcg.git](https://github.com/votre-repo/shimatori-tcg.git)
cd shimatori-tcg
```

### 2. Installer les dépendances 

```bash
pip install -r requirements.txt
```

(*Si vous n'avez pas de fichier requirements.txt, lancez simplement pip install pygame*)

### 3. Lancer le jeu

```bash
python
```


## Commenter jouer 

### Controles
* **Souris (Clique Gauche) :**
    * Glisser-déposer une carte de la main vers le plateau pour la jouer (coûte du Mana).
    * Glisser-déposer une unité alliée vers une cible ennemie pour attaquer.
    * Cliquer sur le bouton "Fin de Tour".

* **Espace :** Passer le tour.
* **Échap :** Retour au menu principal.

## Règles de base

1. Chaque joueur commence avec 30 PV et 1 Mana.
2. Le Mana augmente de 1 à chaque tour (Max 10).
3. Le but est de réduire les PV du héros adverse à 0.
4. Les unités ne peuvent pas attaquer le tour où elles sont jouées (sauf Charge).
5. Si une unité adverse a Provocation, vous devez l'éliminer avant de cibler les autres ou le héros.

# Lore & Factions

Le jeu met en lumière le Clan Hoshikawa ("La Rivière des Étoiles") , un clan noble incarnant le sommet de l'honneur et de la tradition, mis au défi par l'invasion Mongole.

Personnages Clés

* Hoshikawa no Shinsei : L'héritier sacré, né sous une pluie d'étoiles filantes. Protecteur et résilient, il porte le poids du clan.
* Yukihime (L'Hoshikage) : La matriarche redoutée dont l'autorité est absolue.
* Himeno : La jeune sœur médecin, protégée par le clan.
* Harunobu : Le régent militaire, inflexible et brutal.

        "Un Hoshikawa ne cède qu’à l’arène. Et si son clan n’est plus qu’un murmure, alors il sera sa voix la plus pure."

# Crédits : 

**Développé par :**
* Quentin TESTU - Lore & Design
* Enzo GIARDINELLI - Technique et jouabilité

*Projet réalisé dans le cadre du cours de Conception de la POO Avancée - 2025.*
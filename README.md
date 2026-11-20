# Terminal de suppport pour Batifact
Ce projet aide les assistants de support téléphonique de Batifact à retrouver rapidement des fiches de résolution de problème.
Il s'agit d'un terminal dédié où l'on peut lister des fiches.

## Spécifications fonctionnelles

On peut :
- en lire, 
- en écrire (par génération automatique),
- demander à une IA d'en trouver une rapidement selon un contexte donné,
- poser à l'IA des questions sur une fiche.

L'IA peut appeler sur la machine de l'assistant deux fonctions-outils :
- `lire_fiche` pour lire une fiche;
- `ecrire_fiche` pour écrire (générer) une fiche.

L'IA a le droit d'appeler ces 2 fonctions-outils un maximum de fois par question : dix lectures ou écritures de fiche maximum.

Les spécifications détaillées de ce projet sont dans [ces notes](https://github.com/myselfhimself/assistant-fiches-support/blob/main/docs/besoin.md), avec une [demande initiale de la responsable d'équipe ici](https://github.com/myselfhimself/assistant-fiches-support/blob/main/docs/demande-initiale.md).

## Pile technique
- Python >= 3.10
- OpenAI (client Python pointant vers LiteLLM)
- LiteLLM (routeur vers des modèles Claude et ChatGPT)
- Rich (affichage terminal enrichi)

## Installation
Exécuter les commande suivantes :
```sh
python -m venv .venv
source .env/bin/activate
pip install -r requirements.txt
```
### Configuration
Personnaliser le `.env`:
```sh
cp .env.example .env
```

Y insérer la clé API :
```ini
LITELLM_API_KEY="clé API ici"
```

Le fichier `.env` doit bien être ignoré par git. (cf. [.gitignore](.gitignore)].


## Lancement


Lancer un test de connectivité :
```sh
python -m assistant --verifier
```

```sh
python -m assistant

# Ou en mode simulé
SERVICE=simule python -m assistant
```

Prompts à essayer :
```
# Nouveau terminal (remise à zero du contexte)
/nouvelle

# Affichage de l'aide
/aide

# Liste des fiches (de service support) (ces fiches sont dans [fiches/](fiches/)
/fiches

# Question sur une fiche
/joindre facturer-acompte-puis-solde.md Résume cette fiche 10 mots max.

# Question sur toute la fiche, au point que le LLM trouve la bonne et répond avec
Comment faire un export des écritures comptables en très bref?

# Ecriture d'une fiche
Ecris une fiche reinstaller-logiciel-comptable.md qui décrit comme réinstaller le logiciel comptable

# Réécriture d'une fiche (demandera une confirmation avant écriture)
Reprends la fiche reinstaller-logiciel-comptable.md en ajoutant deux démarches différentes pour MacOS et Windows
```

## Tests
Lancer la commande suivante depuis la racine du projet (là où ce fichier se trouve) pour faire tourner la suite de tests :
```sh
pytest
```


# A propos
Projet étudiant de la Wild Code School - parcours DevIA Agentique. Fait à 99% sans IA, mais appelant de l'IA agentique ! :)

# Fiches support : consulter et rédiger les fiches depuis la ligne de commande

La responsable du support de Batifact a validé tes critères d’acceptation. Tu réalises un prototype d’assistant IA en ligne de commande qui répond aux questions de l’équipe à partir des fiches de procédure et rédige de nouvelles fiches, sans agir hors de leur dossier.

Ton prototype répond à ces deux user stories (US) :

> **En tant que** technicien du support Batifact en ligne avec un client, **je veux** poser la question du client à l’assistant, **afin de** suivre la bonne procédure sans chercher la fiche pendant que le client attend.

> **En tant que** technicien du support, **je veux** faire préparer le brouillon d’une fiche manquante, **afin de** ne plus passer une demi-heure à la rédiger.

## Contenu du dépôt

| Fichier | Rôle |
| --- | --- |
| [`assistant/`](assistant/) | Code de départ : chaque `À faire (étape n)` indique ce qui reste à écrire |
| [`assistant/service_simule.py`](assistant/service_simule.py) | Service d’IA simulé, pour essayer et tester sans réseau ni quota : `SERVICE=simule` dans `.env` l’active ; ses questions spéciales sont listées en tête du fichier |
| [`limites.toml`](limites.toml) | Limites fixées par l’équipe |
| [`fiches/`](fiches/) | Fiches de procédure de l’équipe support |
| [`tests/`](tests/) | Tests pytest, dont un premier test fourni, qui réussit une fois l’étape 3 faite |
| [`docs/schema-cadre-technique.md`](docs/schema-cadre-technique.md) | Schéma du cadre technique retenu par l’équipe |
| [`docs/organisation-du-code.md`](docs/organisation-du-code.md) | Package `assistant`, imports et lancement avec `python -m` |
| [`docs/scenario-demonstration.md`](docs/scenario-demonstration.md) | Scénario de la démonstration du vendredi |
| [`.env.example`](.env.example) | Modèle de configuration du service d’IA |
| [`resoudre.py`](resoudre.py) | Rattraper une étape |

## Pour commencer

1. Forke ce dépôt, clone ton fork et ouvre ta demande de fusion (Pull Request) vers ta branche `rendu/<prenom>`, comme au brief précédent : [Fork et demande de fusion](https://github.com/SIMPLON-DIST-DEVIA-P1-199833/assistant-fiches-support/blob/main/docs/github-demande-de-fusion.md) et [Commandes Git](https://github.com/SIMPLON-DIST-DEVIA-P1-199833/assistant-fiches-support/blob/main/docs/git-commandes.md). Pour ce dépôt, les quatre listes de la demande de fusion sont :
   - **base repository :** `SIMPLON-DIST-DEVIA-P1-199833/harness-fiches-support` ;
   - **base :** `rendu/<prenom>`, ta branche ;
   - **head repository :** `<ton-compte>/harness-fiches-support` ;
   - **compare :** `main`.
2. Lis le [schéma du cadre technique](docs/schema-cadre-technique.md) et l’[organisation du code](docs/organisation-du-code.md), puis parcours le code de départ. Une erreur `NotImplementedError: Étape n : …` signale une fonction qu’il reste à écrire à l’étape n.
3. Termine chaque étape par un commit et un push.

## Limites fixées par l’équipe

Le modèle choisit quoi lire et quoi écrire, mais une fiche ou une question peut l’induire en erreur. C’est donc ton code Python qui applique ces limites, avec les valeurs de [`limites.toml`](limites.toml).

| Limite | Pourquoi | Au-delà |
| --- | --- | --- |
| Dossier `fiches/` | Le modèle ne doit lire ni `.env` ni le code | Lecture ou écriture refusée, avec un message |
| Extension `.md` | Les fiches sont en Markdown | Refusée, avec un message |
| 20 Ko par fiche | Une fiche fait environ 1 Ko ; au-delà, elle consomme du quota et encombre la conversation | Lecture ou écriture refusée, jamais tronquée : une procédure coupée perd des étapes |
| 30 s par appel au service | Le technicien est au téléphone avec un client | Question abandonnée avec un message, sans nouvelle tentative ; la conversation continue |
| 10 appels d’outil par question | Un modèle peut tourner en boucle, et chaque appel renvoie toute la conversation | Question arrêtée avec un message ; la conversation continue |
| 60 000 jetons de conversation | Chaque appel renvoie toute la conversation : elle coûte de plus en plus cher et finit par dépasser ce que le modèle accepte | La conversation repart de zéro, avec un message |

## Étapes

### 1. Accès

L’assistant joint le service d’IA de l’entreprise avec ta clé, sans jamais la publier.

1. Crée l’environnement virtuel et installe les dépendances.
2. Configure ta clé dans `.env`.
3. Complète `charger_configuration` dans `assistant/configuration.py`.
4. Vérifie l’accès avec `python -m assistant --verifier`.
5. Décris l’installation dans [Ton assistant](#ton-assistant).

**Résultat :**

> **Étant donné** une clé valide dans `.env`,<br>
> **quand** tu lances `python -m assistant --verifier`,<br>
> **alors** la réponse du service s’affiche.

> **Étant donné** un `.env` sans clé ou sans adresse du service,<br>
> **quand** tu lances l’assistant,<br>
> **alors** un message explique quoi faire.

Lance toujours l’assistant et les tests depuis la racine du dépôt, avec `python -m`. En cas de `ModuleNotFoundError`, voir l’[organisation du code](docs/organisation-du-code.md#erreurs-fréquentes).

<details>
<summary>Indice : environnement</summary>

Créer un environnement virtuel dans le dépôt, l’activer, puis installer les dépendances :

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Voir [Environnements virtuels et paquets](https://docs.python.org/fr/3/tutorial/venv.html).

</details>

<details>
<summary>Indice : clé</summary>

Copier `.env.example` en `.env` et y coller la clé. Avant le premier commit, vérifier que `git status` n’affiche pas `.env`.

Le code de départ charge `.env` avec [python-dotenv](https://pypi.org/project/python-dotenv/) : chaque ligne devient une variable d’environnement du programme. `os.getenv("LITELLM_API_KEY")` renvoie alors ta clé, ou `None` si la variable n’existe pas.

</details>

<details>
<summary>Indice : clé versionnée par erreur</summary>

Supprimer le fichier ne suffit pas : la clé reste dans l’historique. Prévenir le formateur, qui révoque la clé et en donne une nouvelle.

</details>

### 2. Conversation

Le technicien enchaîne les questions pendant un même appel, et une panne du service ne lui fait pas perdre l’assistant.

1. Complète `poser` dans `assistant/conversation.py` : envoie la conversation au service et garde l’historique.
2. Dans `assistant/client.py`, transforme chaque erreur du service en `ServiceIndisponible`.
3. Dans `assistant/interface.py`, affiche ces erreurs sans quitter.
4. Essaie avec `SERVICE=simule` les questions `panne`, `lent` et `refus`.

**Résultat :**

> **Étant donné** une première question posée à l’assistant,<br>
> **quand** le technicien pose une deuxième question qui y renvoie,<br>
> **alors** la réponse en tient compte.

> **Étant donné** `SERVICE=simule` dans `.env`,<br>
> **quand** le technicien pose la question `panne`, `lent` ou `refus`,<br>
> **alors** un message explique le problème, et l’assistant accepte la question suivante.

<details>
<summary>Indice : historique</summary>

Le service ne garde aucune mémoire entre deux appels. À chaque question, tu lui renvoies toute la conversation : la liste `messages`, à laquelle tu ajoutes la question (`"role": "user"`) puis sa réponse (`"role": "assistant"`).

Voir [l’utilisation du SDK OpenAI avec LiteLLM](https://docs.litellm.ai/docs/proxy/user_keys).

</details>

<details>
<summary>Indice : erreurs du service</summary>

Le SDK lève une exception différente pour chaque panne : voir [Handling errors](https://github.com/openai/openai-python#handling-errors). Les transformer en `ServiceIndisponible` avec un message clair, puis afficher ce message dans l’interface. Le principe, sur un autre exemple :

```python
class SaisieInvalide(Exception):
    """La saisie ne permet pas de continuer."""


def lire_age(saisie):
    try:
        return int(saisie)
    except ValueError:
        # Un raise dans le except remplace l’exception par celle du projet.
        raise SaisieInvalide(f"« {saisie} » n’est pas un nombre : saisir l’âge en chiffres.")


try:
    age = lire_age(saisie)
except SaisieInvalide as erreur:  # erreur : l’exception levée
    print(f"Erreur : {erreur}")  # affiche son message
```

</details>

<details>
<summary>Indice : lire un traceback</summary>

Le lire de bas en haut : la dernière ligne donne l’exception, la ligne au-dessus l’endroit du code où elle s’est produite. Formuler une hypothèse, puis la vérifier avec un `print` ou en relançant avec une seule modification.

</details>

### 3. Lecture

Le technicien joint lui-même une fiche à sa question, ou laisse l’assistant choisir la fiche à lire. Ce sont les lignes 2 et 3 du [scénario de démonstration](docs/scenario-demonstration.md) que tu présenteras vendredi.

1. Complète `chemin_autorise` et `lire_fiche` dans `assistant/outils.py`, puis écris leurs tests (fiche du dossier, `..`, chemin absolu) jusqu’à ce que `python -m pytest` réussisse.
2. Ajoute la commande `/joindre <fiche.md> <question>` et complète `joindre_fiche`. Essaie `/joindre facture-non-recue.md Résume cette fiche en trois lignes.`
3. Complète `executer`, puis fais exécuter par `poser` les appels d’outil du modèle jusqu’à sa réponse finale. Essaie la question sur la TVA du scénario.
4. Avec `SERVICE=simule`, vérifie les refus de ton programme : `/joindre ../.env.md Résume-la.` puis `lis ../.env.md`.
5. Dans [Ton assistant](#ton-assistant), compare `/joindre` et `lire_fiche` en quelques lignes.

> [!WARNING]
> Tant que ces refus ne sont pas vérifiés, essaie toute lecture hors du dossier avec `SERVICE=simule` uniquement. Si ton contrôle laisse passer `.env`, son contenu part au service d’IA avec ta clé, et le formateur doit la révoquer.

**Résultat :**

> **Étant donné** que les fiches sont dans le dossier,<br>
> **quand** le technicien demande : « Un client voit 20 % de TVA au lieu de 10 % sur une facture de rénovation, que faire ? »,<br>
> **alors** l’interface signale la lecture, et la réponse reprend les étapes de `modifier-taux-tva.md` en citant son nom.

> **Étant donné** `SERVICE=simule` dans `.env`,<br>
> **quand** le technicien demande `lis ../.env.md`,<br>
> **alors** un message indique que l’accès est refusé, et rien n’est lu.

Tes tests de lecture réussissent avec `python -m pytest`.

<details>
<summary>Indice : appel d’outil</summary>

Voir [Function calling](https://platform.openai.com/docs/guides/function-calling), onglet **Chat Completions**. Le trajet :

1. tu envoies la conversation avec la description des outils (`tools`) ;
2. le modèle répond par des `tool_calls` : nom de l’outil et arguments en JSON ;
3. ton code vérifie les arguments, puis exécute l’outil, ou le refuse ;
4. tu ajoutes la réponse du modèle, puis le résultat (`"role": "tool"`, avec le `tool_call_id`) ;
5. tu renvoies le tout, jusqu’à une réponse sans `tool_calls`.

</details>

<details>
<summary>Indice : signaler et confirmer</summary>

`poser` reçoit deux fonctions de l’interface en paramètres, sans parenthèses : `conversation.poser(…, confirmer, signaler)`. Elles s’appellent comme toute fonction, par exemple `signaler("Fiche lue.")`. Ainsi, `conversation.py` informe l’utilisateur sans dépendre de Rich, et les tests lui passent leurs propres fonctions.

</details>

<details>
<summary>Indice : rester dans le dossier</summary>

Comparer des chaînes de caractères ne suffit pas : `..`, un chemin absolu ou un lien symbolique en sortent. Voir [`Path.resolve()`](https://docs.python.org/fr/3/library/pathlib.html#pathlib.Path.resolve) et [`PurePath.is_relative_to()`](https://docs.python.org/fr/3/library/pathlib.html#pathlib.PurePath.is_relative_to).

</details>

<details>
<summary>Indice : refus et réponses invalides</summary>

Un refus n’arrête pas le programme : il est renvoyé au modèle comme résultat de l’outil, pour que celui-ci puisse répondre à l’utilisateur. Les arguments viennent du modèle : [`json.loads`](https://docs.python.org/fr/3/library/json.html#json.loads), qui lit une chaîne JSON comme `json.load` lit un fichier, peut échouer, une clé peut manquer, l’outil peut ne pas exister. Pour essayer : `SERVICE=simule` et les questions `invalide` et `inconnu`.

</details>

<details>
<summary>Indice : pytest</summary>

Voir [Get Started](https://docs.pytest.org/en/stable/getting-started.html), [pytest.raises](https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions) et [tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html). La fixture `limites` de [`tests/conftest.py`](tests/conftest.py) fournit un dossier de fiches temporaire : tes tests ne modifient pas les vraies fiches.

</details>

### 4. Écriture

Le technicien fait rédiger le brouillon d’une fiche manquante, et aucune fiche existante n’est écrasée sans son accord. Les lignes 4 à 6 du [scénario de démonstration](docs/scenario-demonstration.md) que tu présenteras vendredi en donnent les demandes exactes.

1. Décris l’outil `ecrire_fiche`, puis complète `ecrire_fiche` et `confirmer`. Écris les tests de création et d’écrasement refusé.
2. Dans `poser`, arrête la question au-delà du nombre d’appels d’outil, et repars de zéro au-delà de la taille de conversation, chaque fois avec un message.
3. Essaie avec `SERVICE=simule` : `écris <fiche.md>`, puis `boucle`.
4. Pour essayer la taille de conversation, baisse `conversation_max_jetons` à 300 dans `limites.toml` et enchaîne quelques questions avec `SERVICE=simule`. Remets 60000 avant ton commit.

**Résultat :**

> **Étant donné** qu’aucune fiche `suspendre-compte.md` n’existe,<br>
> **quand** le technicien demande de la rédiger,<br>
> **alors** `fiches/suspendre-compte.md` est créée sans question.

> **Étant donné** que `suspendre-compte.md` existe,<br>
> **quand** le technicien demande de la modifier, puis refuse l’écrasement,<br>
> **alors** un message indique le refus, et la fiche est inchangée.

> **Étant donné** `SERVICE=simule` dans `.env`,<br>
> **quand** le technicien pose la question `boucle`,<br>
> **alors** la question s’arrête au nombre d’appels fixé avec un message, et l’assistant accepte la question suivante.

> **Étant donné** `conversation_max_jetons = 300` et `SERVICE=simule`,<br>
> **quand** le technicien enchaîne quelques questions,<br>
> **alors** un message annonce que la conversation repart de zéro.

Tes tests de création et d’écrasement refusé réussissent.

<details>
<summary>Indice : confirmation</summary>

C’est ton code qui demande la confirmation, pas le modèle. Voir [`Confirm.ask`](https://rich.readthedocs.io/en/stable/prompt.html) de Rich.

</details>

<details>
<summary>Indice : limites</summary>

Compter les appels d’outil d’une même question. Pour la taille de la conversation, chaque réponse du service indique les jetons consommés dans `usage.total_tokens`.

Pour la tester, fixer `limites["conversation_max_jetons"]` à une petite valeur dans le test, puis vérifier le message et la conversation qui repart de zéro.

</details>

### 5. Tests et démonstration

Vendredi, tu présentes ton assistant à Nadia Ferrand, responsable du support, et tes tests montrent qu’il tient ses limites.

1. Complète tes tests avec le service simulé : conversation, appel d’outil, écriture par le modèle, arrêt au nombre d’appels, panne du service.
2. Répète le [scénario de démonstration](docs/scenario-demonstration.md) sur un dépôt propre.

**Résultat :**

> **Étant donné** un dépôt propre,<br>
> **quand** tu lances `python -m pytest`,<br>
> **alors** tous les tests réussissent.

Avec ceux des étapes 3 et 4, tes tests couvrent la lecture, le refus hors dossier, l’écriture, la confirmation, la conversation, l’arrêt au nombre d’appels et la panne du service.

<details>
<summary>Indice : tester avec le service simulé</summary>

Passer au service la liste des réponses qu’il doit renvoyer, dans l’ordre :

```python
from assistant.service_simule import ServiceSimule, appel_outil, texte

service = ServiceSimule([
    appel_outil("lire_fiche", nom="modifier-taux-tva.md"),
    texte("Voir la fiche modifier-taux-tva.md."),
])
```

`service.requetes` garde ensuite les messages reçus à chaque appel.

</details>

**Bonus :** afficher les différences avant un écrasement ([`difflib`](https://docs.python.org/fr/3/library/difflib.html)).

## Rattraper une étape

Si tu restes bloqué·e et que tu veux commencer l’étape suivante, demande le jeton d’accès au formateur, puis lance `python resoudre.py`, environnement du projet activé. Le script contrôle une copie de ton code, indique l’étape en cours et ce qui y manque, puis demande confirmation. Pour choisir l’étape toi-même : `python resoudre.py 3`.

Ton travail est d’abord enregistré dans un commit, puis un second commit corrige les fichiers de code de l’étape avec la version de référence. Tes commits restent dans ton historique ; ton README et les fichiers que tu as ajoutés sont conservés.

## Ton assistant

> À compléter au fil des étapes : installation, configuration de la clé (sans sa valeur), lancement, comportement aux limites, et comparaison de l’étape 3.
>

### Prerequisites
- Tested on local with WSL - Ubuntu
- Python >= 3.11
- Git
- LiteLLM key, provided by the trainer in our case

### Installation
```sh
git clone https://github.com/gavizet/harness-fiches-support.git # clone git repo in current folder
cd harness-fiches-support # navigate to the repository's folder
python3 -m venv .venv # create virtual environment
source .venv/bin/activate # activate the environment
pip install -r requirements.txt # install the dependencies: openai, rich, python-dotenv, pytest
```

### Configuration
Copy example template, then edit `.env`:

```sh
cp .env.example .env
```

| Variable | Required | Value |
| --- | :---: | --- |
| `SERVICE` | No | `litellm` (default): AI service; `simule`: simulated service, no network or quota |
| `LITELLM_BASE_URL` | Yes | Address of the LiteLLM gateway, already filled in `.env.example` |
| `LITELLM_API_KEY` | Yes | Personal LiteLLM key, never paste it or commit it |
| `MODELE` | No | `gpt-luna` (default), `gpt-sol`, `claude-sonnet` or `claude-haiku` |

`.env` is listed in `.gitignore`: never commit it, and NEVER paste the LiteLLM key anywhere other than `.env` file.

If `LITELLM_BASE_URL` or `LITELLM_API_KEY` are missing or empty, the assistant doesn't start and prints which variable to fill in and how.
If `MODELE` is missing, it will default to `gpt-luna`

### Run
Run from the repository's root, with the venv activated (see Installation):

```sh
python3 -m assistant --verifier   # checks access to the AI service, then exits or returns an error if a variable is missing
python3 -m assistant # start the CLI assistant
```
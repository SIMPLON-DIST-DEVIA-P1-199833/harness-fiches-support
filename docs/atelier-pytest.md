# Atelier pytest : tester la conversation

Tu écris les premiers tests automatiques de ton assistant. Ils vérifient la conversation de l’étape 2 avec le service simulé, sans réseau, sans clé et sans consommer ton quota. Tu les compléteras à l’étape 5.

**Résultat attendu :** un fichier `tests/test_conversation.py`, commité et poussé, dont les tests réussissent.

Si `poser` n’est pas encore terminée, tes tests échouent d’abord : ils indiquent ce qui manque. Complète alors `poser` jusqu’à ce qu’ils réussissent.

## 1. Lancer pytest et lire un échec

Environnement du projet activé, à la racine du dépôt, lance :

```sh
python -m pytest
```

pytest cherche dans `tests/` les fichiers `test_*.py`, puis exécute chacune de leurs fonctions `test_…`. Un test réussit si sa fonction se termine sans exception. Un `assert` faux lève une `AssertionError` et fait échouer le test.

Le dépôt contient déjà un test dans `tests/test_outils.py`. Tant que `lire_fiche` n’est pas complétée (étape 3), il échoue. Dans le rapport, repère :

- le nombre de tests réussis et échoués, sur la dernière ligne ;
- le nom du test échoué ;
- les lignes marquées `>` : d’abord dans le test, puis dans le code qu’il appelle ;
- l’exception, sur la ligne `E`.

<details>
<summary>Indice : lancer une partie des tests</summary>

- `python -m pytest tests/test_conversation.py` : un seul fichier.
- `python -m pytest -k refuse` : les tests dont le nom contient « refuse », parmi ceux qui existent déjà.
- `python -m pytest -v` : un test par ligne, avec son résultat.

Voir [Get Started](https://docs.pytest.org/en/stable/getting-started.html).

</details>

## 2. La réponse du modèle

Crée `tests/test_conversation.py`. Écris le test `test_renvoie_la_reponse_du_modele` :

1. prépare un service simulé qui répondra un texte que tu choisis ;
2. démarre une nouvelle conversation ;
3. pose une question avec `poser` et vérifie qu’elle renvoie exactement ce texte.

Lance ce fichier seul. Quand le test réussit, change le texte attendu dans l’`assert`, relance et lis le message d’échec, puis rétablis-le. Un test qui ne peut pas échouer ne vérifie rien.

Tes tests n’appellent jamais le vrai service : ils doivent réussir sans réseau ni `.env`. Voir [le service simulé](service-simule.md).

<details>
<summary>Indice : le service simulé</summary>

`ServiceSimule` reçoit la liste des réponses qu’il doit renvoyer, dans l’ordre : chaque appel au service consomme la suivante. Voir la docstring de [`assistant/service_simule.py`](../assistant/service_simule.py).

```python
from assistant.service_simule import ServiceSimule, texte

service = ServiceSimule([texte("Bonjour, que puis-je faire ?")])
```

</details>

<details>
<summary>Indice : la fixture limites</summary>

Ajoute un paramètre `limites` à ton test : pytest le remplit pour toi.

```python
def test_renvoie_la_reponse_du_modele(limites):
    ...
```

Il prend sa valeur dans [`tests/conftest.py`](../tests/conftest.py), que pytest charge avant tes tests, sans import :

```python
@pytest.fixture
def limites(tmp_path):
    limites = charger_limites()          # les limites de limites.toml
    dossier = tmp_path / "fiches"        # un dossier vide, propre à chaque test
    dossier.mkdir()
    (dossier / "modifier-taux-tva.md").write_text("# Modifier le taux de TVA\n", encoding="utf-8")
    limites["dossier_fiches"] = dossier  # remplace le vrai dossier fiches/
    return limites
```

La ligne `@pytest.fixture` inscrit la fonction auprès de pytest. Avant chaque test qui a un paramètre du même nom, pytest appelle cette fonction et passe le résultat au test. `tmp_path` est fourni par pytest de la même façon.

Ton test reçoit donc le dictionnaire des limites de l’équipe, avec un dossier de fiches temporaire qui ne contient que `modifier-taux-tva.md`. N’appelle pas `charger_limites()` dans un test : il utiliserait le vrai dossier `fiches/`, que tes tests d’écriture modifieraient.

</details>

<details>
<summary>Indice : appeler poser</summary>

`poser` attend les mêmes arguments que dans l’interface. Le nom du modèle importe peu avec le service simulé. Pour `confirmer` et `signaler`, passe deux petites fonctions définies dans ton fichier de test : l’une refuse tout écrasement, l’autre n’affiche rien.

```python
from assistant import conversation


def refuser(nom):
    return False


def ignorer(texte):
    pass


messages = conversation.nouvelle_conversation(limites)
reponse = conversation.poser("Bonjour", messages, service, "simule", limites, refuser, ignorer)
```

</details>

## 3. L’historique

Écris `test_garde_l_historique` : pose deux questions dans la même conversation, puis vérifie que le service a reçu, lors du deuxième appel, la première question et sa réponse. Pour lancer ce seul test : `python -m pytest -k historique`.

Vérifie ensuite que ce test détecte un vrai défaut : dans `poser`, mets en commentaire la ligne qui ajoute la réponse du modèle à `messages`, relance, puis rétablis la ligne.

<details>
<summary>Indice : ce que le service a reçu</summary>

`service.requetes` garde une entrée par appel, dans l’ordre. `service.requetes[1]["messages"]` est la liste des messages reçus au deuxième appel, chacun sous la forme `{"role": …, "content": …}`.

Une compréhension de liste en extrait les textes, puis `in` vérifie la présence d’un élément :

```python
contenus = [m["content"] for m in service.requetes[1]["messages"]]
assert "Bonjour" in contenus
```

</details>

## 4. Les pannes du service

1. Écris un test qui vérifie qu’une panne du service fait lever `ServiceIndisponible` par `poser`. Fais de même pour un délai dépassé et pour une clé refusée.
2. Ces tests ne vérifient pas l’interface. Mets `SERVICE=simule` dans `.env`, lance l’assistant et pose les questions `panne`, `lent` et `refus`, puis une question ordinaire.

**Résultat :**

> **Étant donné** `SERVICE=simule` dans `.env`,<br>
> **quand** tu poses la question `panne` dans l’assistant,<br>
> **alors** un message s’affiche, et l’assistant accepte la question suivante.

<details>
<summary>Indice : attendre une exception</summary>

Un test réussit s’il se termine sans exception. Pour vérifier qu’une exception est levée, utilise `pytest.raises` : le test échoue si le bloc ne la lève pas. Les erreurs prévues `panne()`, `delai_depasse()` et `cle_refusee()` sont dans `assistant/service_simule.py`.

```python
import pytest

from assistant import client
from assistant.service_simule import panne

service = ServiceSimule([panne()])
with pytest.raises(client.ServiceIndisponible):
    ...  # l’appel qui doit lever l’exception
```

Voir [pytest.raises](https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions).

</details>

<details>
<summary>Indice : un test, trois pannes</summary>

`@pytest.mark.parametrize` lance le même test avec chaque valeur de la liste, reçue en paramètre :

```python
@pytest.mark.parametrize("erreur", [panne(), delai_depasse(), cle_refusee()])
def test_une_panne_leve_service_indisponible(limites, erreur):
    ...
```

Voir [parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html).

</details>

## 5. Pour aller plus loin

Après une panne, le technicien doit savoir quoi faire. Pour chaque panne, vérifie que le message de `ServiceIndisponible` le lui dit. Par exemple, pour une clé refusée, le message cite `LITELLM_API_KEY`.

<details>
<summary>Indice : lire le message d’une exception</summary>

`pytest.raises(…) as erreur` garde l’exception levée dans `erreur.value`, et `str(erreur.value)` donne son message :

```python
with pytest.raises(client.ServiceIndisponible) as erreur:
    ...  # l’appel qui doit lever l’exception
assert "LITELLM_API_KEY" in str(erreur.value)
```

</details>

## 6. Commit

Commite `tests/test_conversation.py`, avec `poser` si tu l’as complétée, puis pousse.

**Résultat :**

> **Étant donné** ton fichier `tests/test_conversation.py`,<br>
> **quand** tu lances `python -m pytest tests/test_conversation.py`,<br>
> **alors** tes tests de réponse, d’historique et de pannes réussissent, sans réseau ni clé.

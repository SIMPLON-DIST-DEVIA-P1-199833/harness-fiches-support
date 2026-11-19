# Le service simulé

Le service simulé remplace le service d’IA par un faux service écrit en Python, qui tourne sur ta machine. Il sert à essayer ton assistant et à le tester sans réseau, sans clé et sans consommer ton quota.

## Pourquoi un faux service

|  | Vrai service (passerelle LiteLLM) | Service simulé |
| --- | --- | --- |
| Réseau et clé | nécessaires | inutiles |
| Quota | consommé à chaque question | jamais consommé |
| Réponses | différentes d’un essai à l’autre | toujours les mêmes |
| Panne, délai dépassé, clé refusée | impossibles à provoquer à volonté | sur demande |
| Appel d’outil, arguments mal formés | quand le modèle le décide | sur demande |

Pour vérifier que ton programme réagit bien à une panne ou à un appel d’outil, il faut pouvoir la provoquer, à chaque essai, de la même façon. Le vrai service ne le permet pas.

## Ton code ne change pas

`ServiceSimule` s’utilise exactement comme le client OpenAI : `service.chat.completions.create(model=…, messages=…)`. Il renvoie les mêmes réponses et lève les mêmes exceptions que le SDK.

Le choix se fait une seule fois, au démarrage, dans `creer_client` (`assistant/client.py`), d’après la variable `SERVICE` de `.env`. Ensuite, `poser` et `envoyer` reçoivent un objet `service` sans savoir lequel des deux c’est.

```mermaid
flowchart TB
    ENV[".env<br>SERVICE=…"] --> CC["creer_client<br>au démarrage"]
    CC -->|"litellm"| OA["client OpenAI"]
    CC -->|"simule"| SS["ServiceSimule<br>sur ta machine"]
    OA -.->|"réseau, clé, quota"| GW["passerelle LiteLLM<br>puis modèle"]
    OA --> SVC(["objet service"])
    SS --> SVC
    SVC --> P["poser puis envoyer<br>service.chat.completions.create(…)"]
```

## Deux façons de l’utiliser

### Essayer à la main : `SERVICE=simule`

Mets `SERVICE=simule` dans `.env`, puis lance l’assistant. Le service simulé cherche un mot-clé dans la première ligne de ta question pour choisir sa réponse : `panne`, `lent`, `refus`, `lis <fiche.md>`, `écris <fiche.md>`, `boucle`, `invalide`, `inconnu`. Sans mot-clé, il renvoie un texte. La liste complète est en tête de [`assistant/service_simule.py`](../assistant/service_simule.py).

```mermaid
sequenceDiagram
    actor Toi
    participant I as interface.py
    participant P as poser et envoyer
    participant S as ServiceSimule
    Toi->>I: panne
    I->>P: question
    P->>S: create(messages)
    Note over S: mot-clé « panne »
    S--)P: lève APIConnectionError
    P--)I: lève ServiceIndisponible
    I->>Toi: message d’erreur, puis question suivante
```

Tu vérifies ce que **tu vois** : le message affiché, l’assistant qui continue.

### Vérifier automatiquement : `ServiceSimule([…])` dans un test

Dans un test, tu crées toi-même le service avec la liste des réponses qu’il doit renvoyer, dans l’ordre. `SERVICE` et `.env` ne jouent aucun rôle : le test passe le service directement à `poser`. Après l’appel, `service.requetes` garde ce que le service a reçu.

```mermaid
sequenceDiagram
    participant T as Ton test
    participant P as poser
    participant S as ServiceSimule
    T->>S: ServiceSimule([texte("A"), panne()])
    T->>P: poser("Question 1", …, service, …)
    P->>S: create(messages)
    Note over S: requetes[0] = messages reçus
    S-->>P: texte « A »
    P-->>T: renvoie « A »
    T->>P: poser("Question 2", …, service, …)
    P->>S: create(messages)
    Note over S: requetes[1] = messages reçus
    S--)P: lève APIConnectionError
    P--)T: lève ServiceIndisponible
    Note over T: assert sur les réponses, les exceptions et service.requetes
```

```python
from assistant.service_simule import ServiceSimule, panne, texte

service = ServiceSimule([texte("A"), panne()])
```

Ton test vérifie ce que **ton code fait** : ce qu’il renvoie, ce qu’il lève, ce qu’il a envoyé au service.

## À retenir

- Un test n’appelle jamais le vrai service : il doit réussir sans réseau, sans clé et sans `.env`.
- `SERVICE=simule` sert à essayer à la main, `ServiceSimule([…])` sert dans les tests.
- Avant la démonstration, remets `SERVICE=litellm` dans `.env`.

"""Service d’IA simulé : mêmes réponses et mêmes erreurs que la passerelle, sans réseau ni quota.

Deux usages :
• dans l’assistant, avec SERVICE=simule dans .env : la réponse dépend des mots-clés de ta question ;
• dans les tests : ServiceSimule([...]) renvoie les réponses prévues, dans l’ordre.

Mots-clés reconnus dans la première ligne de ta dernière question :
    lis <fiche.md>     le modèle appelle lire_fiche
    écris <fiche.md>   le modèle appelle ecrire_fiche avec un brouillon
    boucle             le modèle appelle lire_fiche à chaque tour, sans s’arrêter
    invalide           le modèle appelle un outil avec des arguments mal formés
    inconnu            le modèle appelle un outil qui n’existe pas
    panne              le service est injoignable
    lent               le service ne répond pas dans le délai
    refus              la clé est refusée
Sans mot-clé, il répond par un texte. Après un résultat d’outil, il le résume.
"""

import copy
import json
import re
from types import SimpleNamespace

import httpx2
import openai
from openai.types.chat import ChatCompletion

URL_SIMULEE = "http://service-simule/v1/chat/completions"

BROUILLON = """# Brouillon de fiche

## Symptôme

À préciser.

## Étapes

1. À préciser.

## Vérification

À préciser.
"""


def texte(contenu):
    """Réponse prévue : un texte du modèle."""
    return {"texte": contenu}


def appel_outil(outil, **arguments):
    """Réponse prévue : un appel d’outil aux arguments bien formés."""
    return {"outil": outil, "arguments": json.dumps(arguments, ensure_ascii=False)}


def appel_mal_forme(outil, arguments):
    """Réponse prévue : un appel d’outil dont les arguments sont le texte brut donné."""
    return {"outil": outil, "arguments": arguments}


def panne():
    """Erreur prévue : service injoignable."""
    return openai.APIConnectionError(request=httpx2.Request("POST", URL_SIMULEE))


def delai_depasse():
    """Erreur prévue : délai dépassé."""
    return openai.APITimeoutError(request=httpx2.Request("POST", URL_SIMULEE))


def cle_refusee():
    """Erreur prévue : clé refusée par la passerelle."""
    requete = httpx2.Request("POST", URL_SIMULEE)
    return openai.AuthenticationError("Clé refusée", response=httpx2.Response(401, request=requete), body=None)


class ServiceSimule:
    """S’utilise comme le client OpenAI : client.chat.completions.create(model=..., messages=...)."""

    def __init__(self, reponses=None):
        self.reponses = None if reponses is None else list(reponses)
        self.requetes = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._creer))
        self._appels = 0

    def _creer(self, model, messages, tools=None, **options):
        # Comme le SDK, accepte les messages du modèle tels que reçus, sans conversion en dictionnaire.
        messages = [m.model_dump(exclude_none=True) if hasattr(m, "model_dump") else m for m in messages]
        self.requetes.append({"messages": copy.deepcopy(messages), "tools": tools})
        if self.reponses is None:
            prevue = self._selon_mots_cles(messages)
        elif self.reponses:
            prevue = self.reponses.pop(0)
        else:
            raise RuntimeError("Service simulé : plus aucune réponse prévue.")
        if isinstance(prevue, Exception):
            raise prevue
        return self._completion(model, messages, prevue)

    def _selon_mots_cles(self, messages):
        question = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "").split("\n")[0]
        mots = set(re.findall(r"\w+", question.lower()))
        dernier = messages[-1]
        fiche = re.search(r"\S+\.md\b", question)
        nom = fiche.group(0) if fiche else "reinitialiser-mot-de-passe.md"
        if "panne" in mots:
            return panne()
        if "lent" in mots:
            return delai_depasse()
        if "refus" in mots:
            return cle_refusee()
        if "boucle" in mots:
            return appel_outil("lire_fiche", nom=nom)
        if dernier["role"] == "tool":
            return texte(f"Réponse simulée, d’après le résultat de l’outil : {dernier['content'][:300]}")
        if "invalide" in mots:
            return appel_mal_forme("lire_fiche", '{"nom": ')
        if "inconnu" in mots:
            return appel_outil("supprimer_fiche", nom=nom)
        if "lis" in mots:
            return appel_outil("lire_fiche", nom=nom)
        if "écris" in mots:
            return appel_outil("ecrire_fiche", nom=nom, contenu=BROUILLON)
        return texte(f"Réponse simulée à : {question[:300]}")

    def _completion(self, model, messages, prevue):
        if "texte" in prevue:
            message = {"role": "assistant", "content": prevue["texte"]}
            fin = "stop"
        else:
            self._appels += 1
            appel = {
                "id": f"appel-{self._appels}",
                "type": "function",
                "function": {"name": prevue["outil"], "arguments": prevue["arguments"]},
            }
            message = {"role": "assistant", "content": None, "tool_calls": [appel]}
            fin = "tool_calls"
        jetons = len(json.dumps(messages, ensure_ascii=False)) // 4
        return ChatCompletion.model_validate({
            "id": "simulation",
            "object": "chat.completion",
            "created": 0,
            "model": model,
            "choices": [{"index": 0, "finish_reason": fin, "message": message}],
            "usage": {"prompt_tokens": jetons, "completion_tokens": 20, "total_tokens": jetons + 20},
        })

"""Échanges avec le service d’IA, réel ou simulé."""

import openai

from assistant.service_simule import ServiceSimule


class ServiceIndisponible(Exception):
    """Le service n’a pas fourni de réponse utilisable."""


def creer_client(configuration, limites):
    """Renvoie le client du service choisi dans la configuration."""
    if configuration["service"] == "simule":
        return ServiceSimule()
    return openai.OpenAI(
        base_url=configuration["url"],
        api_key=configuration["cle"],
        timeout=limites["delai_s"],
        max_retries=0,
    )


def envoyer(client, modele, messages, outils=None):
    """Envoie les messages au service et renvoie sa réponse, ou lève ServiceIndisponible."""
    options = {"model": modele, "messages": messages}
    if outils:
        options["tools"] = outils
    # À faire (étape 2) : transformer chaque erreur du service en ServiceIndisponible,
    # avec un message qui dit à l’utilisateur ce qui se passe et quoi faire.
    return client.chat.completions.create(**options)


def verifier_acces(client, modele):
    """Envoie une demande minimale et renvoie le texte de la réponse."""
    reponse = envoyer(client, modele, [{"role": "user", "content": "Réponds seulement : accès vérifié."}])
    return reponse.choices[0].message.content

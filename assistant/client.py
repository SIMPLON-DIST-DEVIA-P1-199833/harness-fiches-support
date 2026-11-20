"""Échanges avec le service d’IA, réel ou simulé."""

import openai

from assistant.configuration import ConfigurationInvalide
from assistant.service_simule import ServiceSimule


class ServiceIndisponible(Exception):
    """Le service n’a pas fourni de réponse utilisable."""


def creer_client(configuration, limites):
    """Renvoie le client du service choisi dans la configuration."""
    if configuration["service"] == "simule":
        return ServiceSimule()
    # Sans adresse, le SDK enverrait la clé à OpenAI : refuser avant tout appel.
    if not configuration.get("url"):
        raise ConfigurationInvalide(
            "Adresse du service absente : vérifie LITELLM_BASE_URL dans .env et ce que renvoie charger_configuration."
        )
    # Arguments nommés (nom=valeur) : chacun désigne son paramètre, dans n’importe quel ordre.
    return openai.OpenAI(
        base_url=configuration["url"],
        api_key=configuration["cle"],
        timeout=limites["delai_s"],
        max_retries=0,
    )


def envoyer(client, modele, messages, outils=None):
    """Envoie les messages au service et renvoie sa réponse, ou lève ServiceIndisponible."""
    try:
        if outils:
            reponse = client.chat.completions.create(
                model=modele, messages=messages, tools=outils
            )
        else:
            reponse = client.chat.completions.create(model=modele, messages=messages)
    except openai.APITimeoutError:
        raise ServiceIndisponible("Délai dépassé : réessayer")
    except openai.APIConnectionError as e:
        raise ServiceIndisponible(
            "Service injoignable : vérifier la connexion et LITELLM_BASE_URL"
        )
    except openai.AuthenticationError:
        raise ServiceIndisponible("Clé refusée : vérifier LITELLM_API_KEY dans .env")
    except openai.APIError:
        raise ServiceIndisponible("Erreur du service : contacter le HelpDesk")
    return reponse


def verifier_acces(client, modele):
    """Envoie une demande minimale et renvoie le texte de la réponse."""
    reponse = envoyer(
        client,
        modele,
        [{"role": "user", "content": "Réponds seulement : accès vérifié."}],
    )
    # La réponse est un objet du SDK : ses champs se lisent avec un point, pas avec ["..."].
    return reponse.choices[0].message.content

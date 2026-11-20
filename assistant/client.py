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
        raise ConfigurationInvalide("Adresse du service absente : vérifie LITELLM_BASE_URL dans .env et ce que renvoie charger_configuration.")
    # Arguments nommés (nom=valeur) : chacun désigne son paramètre, dans n’importe quel ordre.
    return openai.OpenAI(
        base_url=configuration["url"],
        api_key=configuration["cle"],
        timeout=limites["delai_s"],
        max_retries=0,
    )


def envoyer(client, modele, messages, outils=None):
    """Envoie les messages au service et renvoie sa réponse, ou lève ServiceIndisponible."""
    # À faire (étape 2) [fait] : transformer chaque erreur du service en ServiceIndisponible,
    # avec un message qui dit à l’utilisateur ce qui se passe et quoi faire.
    try: 
        if outils:
            reponse = client.chat.completions.create(model=modele, messages=messages, tools=outils)
        else:
            reponse = client.chat.completions.create(model=modele, messages=messages)
        return reponse
    except openai.APITimeoutError as e:
        raise ServiceIndisponible("Pas de réponse dans le délai, la question est abandonnée. Veuillez reposer la question") from e
    except openai.APIConnectionError as e:
        raise ServiceIndisponible("Service injoignable. Vérifier le réseau ou prévenir le responsable.") from e
    except openai.AuthenticationError as e:
        raise ServiceIndisponible("Clé API refusée. Vérifier LITELLM_API_KEY dans .env") from e
    except openai.APIError as e:
        raise ServiceIndisponible("Le service a renvoyé une erreur. Vous pouvez réessayer ou contacter un responsable") from e


def verifier_acces(client, modele):
    """Envoie une demande minimale et renvoie le texte de la réponse."""
    reponse = envoyer(client, modele, [{"role": "user", "content": "Réponds seulement : accès vérifié."}])
    # La réponse est un objet du SDK : ses champs se lisent avec un point, pas avec ["..."].
    return reponse.choices[0].message.content

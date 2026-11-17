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


# Resource: https://github.com/openai/openai-python#handling-errors
# See https://github.com/openai/openai-python/blob/v3.50.0/src/openai/_exceptions.py#L46-L161 for openai python module Exception inheritance
def envoyer(client, modele, messages, outils=None):
    """Envoie les messages au service et renvoie sa réponse, ou lève ServiceIndisponible."""
    try:
        if outils:
            reponse = client.chat.completions.create(
                model=modele, messages=messages, tools=outils
            )
        else:
            reponse = client.chat.completions.create(model=modele, messages=messages)
    # Catch all exceptions from openai module separately, and raise them as ServiceIndisponible with a message detailing the problem
    # Using `raise ... from ...` form to chain the Exceptions explicitely
    # Most specific (children) Exceptions are handled first
    except openai.APITimeoutError as error:
        raise ServiceIndisponible(
            "AI service did not answer in time. Ask again"
        ) from error
    except openai.APIConnectionError as error:
        raise ServiceIndisponible(
            "AI service could not be reached. Check connection and LITELLM_BASE_URL in .env."
        ) from error
    except openai.AuthenticationError as error:
        raise ServiceIndisponible(
            "AI service refused the API key. Check LITELLM_API_KEY in .env."
        ) from error
    except openai.RateLimitError as error:
        raise ServiceIndisponible(
            "You reached the quota of your API key, try again later."
        ) from error
    # We handle absent/empty MODEL with our default constant, but still need this to handle badly written models names / urls
    except openai.NotFoundError as error:
        raise ServiceIndisponible(
            "NotFound: check MODELE and LITELLM_BASE_URL in .env."
        ) from error
    except openai.APIStatusError as error:
        raise ServiceIndisponible(
            f"AI service returned an error (HTTP {error.status_code}), try again."
        ) from error
    except openai.APIError as error:
        raise ServiceIndisponible("AI service returned an error, try again.") from error
    # Invalid response (empty) should still produce a message
    if not reponse.choices:
        raise ServiceIndisponible("AI service returned an empty response. Ask again.")
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

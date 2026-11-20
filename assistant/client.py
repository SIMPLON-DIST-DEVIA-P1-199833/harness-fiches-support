"""Échanges avec le service d’IA, réel ou simulé."""

import openai

from assistant.configuration import ConfigurationInvalide
from assistant.service_simule import ServiceSimule


class ServiceIndisponible(Exception):
    """Le service n’a pas fourni de réponse utilisable."""


def creer_client(configuration, limites) -> openai.OpenAI | ServiceSimule:
    """Renvoie le client du service choisi dans la configuration."""
    if configuration["service"] == "simule":
        return ServiceSimule()
    # Sans adresse, le SDK enverrait la clé à OpenAI : refuser avant tout appel.
    if not configuration.get("url"):
        raise ConfigurationInvalide(
            "Adresse du service absente : vérifie LITELLM_BASE_URL dans .env et ce que renvoie charger_configuration."
        )
    # Arguments nommés (nom=valeur) : chacun désigne son paramètre, dans n’importe quel ordre.
    try:
        client = openai.OpenAI(
            base_url=configuration["url"],
            api_key=configuration["cle"],
            timeout=limites["delai_s"],
            max_retries=0,
        )
    except (openai.OpenAIError, TypeError, ValueError) as e:
        raise ConfigurationInvalide(f"Création impossible du client OpenAI ({e})")
    return client


def envoyer(
    client: openai.OpenAI | ServiceSimule,
    modele: str,
    messages: list,
    outils: None | list = None,
):
    """Envoie les messages au service et renvoie sa réponse, ou lève ServiceIndisponible."""
    # À faire (étape 2) : transformer chaque erreur du service en ServiceIndisponible,
    # avec un message qui dit à l’utilisateur ce qui se passe et quoi faire.
    try:
        # images_response = client.images.generate(**image_params)

        if outils:
            reponse = client.chat.completions.create(
                model=modele, messages=messages, tools=outils
            )
        else:
            reponse = client.chat.completions.create(model=modele, messages=messages)
    # Exception catching grasped from https://community.openai.com/t/how-to-do-exception-testing-since-the-update/564474/2
    except openai.AuthenticationError as e:
        raise ConfigurationInvalide(f"Authentification OpenAI impossible ({e})")
    except openai.APITimeoutError as e:
        raise ServiceIndisponible(
            f"Serveur trop lent à répondre. Réessayer plus tard. ({e.message})"
        )
    except openai.APIConnectionError as e:
        raise ServiceIndisponible(
            f"Pensez à revoir vos réglages de connexion au serveur (.env). (Server connection error: {e.message})"
        )
    except openai.RateLimitError as e:
        raise ServiceIndisponible(
            f"Vos demandes sont trop fréquentes. Attendez un peu. (OpenAI RATE LIMIT error {e.status_code}: {e.response})"
        )
    except openai.APIStatusError as e:
        raise ServiceIndisponible(
            f"Le serveur de chat a un souci ou est mal appelé. Contactez votre administrateur. (OpenAI STATUS error {e.status_code}: {e.response})"
        )
    except openai.APIError as e:
        raise ServiceIndisponible(
            f"Erreur non traitée. Contactez votre administrateur. (OpenAI uncaught error: {e})"
        )

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

"""Configuration de l’assistant : service d’IA dans .env, limites dans limites.toml."""

import os
import re
import tomllib
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse

from dotenv import load_dotenv

# __file__ : chemin de ce fichier ; resolve() le rend absolu, chaque .parent remonte d’un dossier.
RACINE = Path(__file__).resolve().parent.parent

Limites = TypedDict(
    "Limites",
    {
        "dossier_fiches": str,
        "extension": str,
        "taille_max_ko": int,
        "delai_s": int,
        "appels_outil_max": int,
        "conversations_max_jetons": int,
    },
)


# Exception propre au projet : raise ConfigurationInvalide("message"), puis except ConfigurationInvalide.
class ConfigurationInvalide(Exception):
    """La configuration ne permet pas de démarrer l’assistant."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"Configuration: {self.message}"


# Entre deux Path, ou un Path et une chaîne, / assemble un chemin.
def charger_limites(chemin=RACINE / "limites.toml") -> Limites:
    """Renvoie les limites de limites.toml dans un dictionnaire."""
    with open(
        chemin, "rb"
    ) as fichier:  # "rb" : lecture en binaire, demandée par tomllibal
        limites = tomllib.load(fichier)
    limites["dossier_fiches"] = RACINE / limites["dossier_fiches"]
    return limites  # pyright: ignore[reportReturnType]


def charger_configuration():
    """Lit .env et renvoie la configuration du service d’IA dans un dictionnaire."""
    if not load_dotenv(RACINE / ".env"):
        raise ConfigurationInvalide(
            ".env manquant, créer ce fichier à partir de .env.example"
        )
    service = os.getenv(
        "SERVICE", "litellm"
    )  # variable d’environnement SERVICE, sinon "litellm"
    if service == "simule":
        return {"service": "simule", "modele": "simule"}
    # À faire (étape 1) : lire LITELLM_API_KEY, LITELLM_BASE_URL et MODELE ;
    try:
        api_key = os.environ["LITELLM_API_KEY"].strip()
        api_url = os.environ["LITELLM_BASE_URL"].strip()
        model = os.environ["MODELE"].strip()
    except KeyError as e:
        raise ConfigurationInvalide(f"Clé manquante ({e}): éditer .env")
    if not api_key.startswith("sk-"):
        raise ConfigurationInvalide(
            "API Key LiteLLM vide ou malformattée (LITELLM_API_KEY): éditer .env"
        )
    result = urlparse(api_url)
    if not all([result.scheme, result.netloc]):
        raise ConfigurationInvalide("URL LiteLLM malformatté ou mal encodé (LITELLM_BASE_URL): éditer .env")
    if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$", model):
        raise ConfigurationInvalide("nom de modèle non valide (MODELE): éditer .env")
    return {"service": service, "url": api_url, "cle": api_key, "modele": model}
